from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from consensus_workbench.agenda.item_contract import ContractError, Decision, DomainRecord, records_from_fixture, stable_hash
from consensus_workbench.records.deliberation_store import Repository
from consensus_workbench.ballots.vote_governance import advance_for_outcome, decide
from consensus_workbench.resolutions.resolution_pack import export_bundle, verify_bundle
from consensus_workbench.evidence.evidence_match import derive_context
from consensus_workbench.grouping.evidence_groups import DEFAULT_ROSTER_SIZE
from consensus_workbench.grouping.sealed_report import (
    build_analysis,
    list_sealed_analyses,
    seal_analysis,
    verify_analysis_index,
    verify_sealed_analysis,
)

from consensus_workbench.consensus_signal.consensus_readiness import augment_context

class Application:
    def __init__(self, database: str | Path, context: Mapping[str, Any] | None = None):
        self.repository = Repository(database)
        self.context = dict(context or {})

    def ingest(self, record: DomainRecord) -> DomainRecord:
        current = self.repository.get_record(record.record_id)
        if current is None:
            self.repository.save_record(record)
            return record
        if current.fingerprint == record.fingerprint:
            return current
        replacement = DomainRecord(record.record_id, record.payload, current.state,
                                   current.version + 1, record.occurred_at, record.source)
        self.repository.save_record(replacement, expected_version=current.version)
        return replacement

    def process(self, record: DomainRecord) -> tuple[DomainRecord, Decision]:
        stored = self.ingest(record)
        context = dict(self.context)
        context.update(derive_context(stored, self.repository))
        context.update(augment_context(stored, self.repository))
        decision = decide(stored, context)
        self.repository.save_decision(decision)
        advanced = advance_for_outcome(stored, decision)
        if advanced.fingerprint != stored.fingerprint:
            self.repository.save_record(advanced, expected_version=stored.version)
        return advanced, decision

    def run_fixture(self, fixture: Mapping[str, Any], output: str | Path) -> dict[str, Any]:
        records = records_from_fixture(fixture)
        fixture_hash = stable_hash(fixture)
        run_id = self.repository.begin_run(fixture_hash, len(records))
        completed = self.repository.completed_run(run_id)
        if completed is not None:
            return completed
        decisions: dict[str, Decision] = {}
        final_records: list[DomainRecord] = []
        for record in records:
            final_record, decision = self.process(record)
            final_records.append(final_record)
            decisions[record.record_id] = decision
        snapshot = self.repository.snapshot()
        if snapshot["chain_errors"]:
            raise ContractError("audit chain verification failed")
        manifest = export_bundle(output, final_records, decisions, snapshot, self.repository.event_rows())
        result = {"run_id": run_id, "fixture_hash": fixture_hash, "records": len(final_records),
                  "decisions": len(decisions), "manifest": manifest, "snapshot": snapshot}
        self.repository.finish_run(run_id, result)
        return result

    def inspect(self) -> dict[str, Any]:
        return {"snapshot": self.repository.snapshot(), "records": [record.__dict__ for record in self.repository.list_records()],
                "decisions": self.repository.decision_rows()}

    def analyze(self, analysis_dir: str | Path,
                roster_size: int = DEFAULT_ROSTER_SIZE,
                roster_override: list[str] | None = None) -> dict[str, Any]:
        """对封存库当前状态生成分组共识分析，并只追加封存（绝不改写历史）。

        分析读取的是已封存的记录版本与决定；后续补录产生新版本后再次调用只会
        追加一份新分析，旧报告及其哈希链保持不变、仍可独立核验。
        """
        run = self.repository.latest_run()
        if run is None:
            raise ContractError("no sealed run found; run the fixture before analysis")
        records = self.repository.list_records()
        if not records:
            raise ContractError("no sealed records available for analysis")
        decisions = self.repository.decisions_by_record()
        missing = sorted(set(record.record_id for record in records) - set(decisions))
        if missing:
            raise ContractError(f"sealed records without decisions: {missing}")
        body = build_analysis(records, decisions, run["fixture_hash"], run["run_id"],
                              roster_size=roster_size, roster_override=roster_override)
        envelope = seal_analysis(analysis_dir, body)
        return {"analysis_id": envelope["analysis_id"], "body_hash": envelope["body_hash"],
                "chain_hash": envelope["chain_hash"], "run_id": run["run_id"],
                "fixture_hash": run["fixture_hash"],
                "analysis_dir": str(analysis_dir),
                "sealed_analyses": len(list_sealed_analyses(analysis_dir))}


def load_fixture(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read fixture: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("fixture root must be an object")
    return value


def run(fixture_path: str | Path, database: str | Path, output: str | Path,
        context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return Application(database, context).run_fixture(load_fixture(fixture_path), output)


def analyze(database: str | Path, analysis_dir: str | Path,
            roster_size: int = DEFAULT_ROSTER_SIZE,
            roster_override: list[str] | None = None) -> dict[str, Any]:
    return Application(database).analyze(analysis_dir, roster_size=roster_size,
                                         roster_override=roster_override)


def verify(database: str | Path, output: str | Path,
           analysis_dir: str | Path | None = None) -> dict[str, Any]:
    repository = Repository(database)
    chain_errors = repository.verify_chain()
    bundle_errors = verify_bundle(output)
    result = {"ok": not chain_errors and not bundle_errors, "chain_errors": chain_errors,
              "bundle_errors": bundle_errors, "snapshot": repository.snapshot()}
    if analysis_dir is not None:
        index_errors = verify_analysis_index(analysis_dir)
        report_errors: list[str] = []
        for entry in list_sealed_analyses(analysis_dir):
            report = verify_sealed_analysis(analysis_dir, entry["analysis_id"], repository)
            report_errors.extend(f"{entry['analysis_id']}: {error}"
                                 for error in report["errors"])
        analysis_errors = index_errors + report_errors
        result["analysis_dir"] = str(analysis_dir)
        result["analysis_errors"] = analysis_errors
        result["ok"] = result["ok"] and not analysis_errors
    return result
