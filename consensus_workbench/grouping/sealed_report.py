"""分组共识分析的封存与核验。

封存语义（对应“后续补录不能让先前已封存的结论无声改变”）：

* 每次分析写成一个**只追加**的报告文件
  ``analysis-<analysis_id>.json``，文件名即其确定性内容哈希；已存在则直接复用，
  绝不覆盖。
* 报告主体（``body``）不含任何时间戳，其 sha256 即 ``body_hash``，同一输入在
  任意时间、任意机器上重算得到同一哈希；时间戳只放在外层封皮，不参与主体哈希。
* 目录下的 ``analysis-index.json`` 是哈希链：每条记录的 ``chain_hash`` 覆盖
  前一条链哈希与本条 body_hash，追加新报告只能延长链，无法在不被发现的情况
  下插入或改写历史条目。
* 每条报告回链封存库中的 fixture_hash、run_id、record_id/version/fingerprint
  与 decision_id，可逐项核验到原始记录与版本。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from consensus_workbench.agenda.item_contract import (
    Decision,
    DomainRecord,
    stable_hash,
    utc_now,
)
from consensus_workbench.grouping.evidence_groups import (
    DEFAULT_ROSTER_SIZE,
    build_group_report,
    fingerprint_index,
)
from consensus_workbench.grouping.influence_analysis import build_influence_report

ANALYSIS_VERSION = 1
INDEX_NAME = "analysis-index.json"
GENESIS_HASH = "0" * 64


def build_analysis(records: Iterable[DomainRecord],
                   decisions: Mapping[str, Decision],
                   fixture_hash: str,
                   run_id: str,
                   roster_size: int = DEFAULT_ROSTER_SIZE,
                   roster_override: Sequence[str] | None = None) -> dict[str, Any]:
    """构造不含时间戳的确定性分析主体（封存内容本体）。"""
    records = sorted(records, key=lambda item: item.record_id)
    group_report = build_group_report(records, roster_size, roster_override)
    influence = build_influence_report(group_report, records, decisions)

    decision_refs = {
        record_id: {
            "decision_id": decision.fingerprint,
            "outcome": decision.outcome,
            "score": decision.score,
        }
        for record_id, decision in sorted(decisions.items())
    }
    traceability = {
        "fixture_hash": fixture_hash,
        "run_id": run_id,
        "record_refs": fingerprint_index(group_report),
        "decision_refs": decision_refs,
    }
    return {
        "analysis_version": ANALYSIS_VERSION,
        "fixture_hash": fixture_hash,
        "run_id": run_id,
        "group_consensus": group_report,
        "influence": influence,
        "traceability": traceability,
    }


def analysis_identity(body: Mapping[str, Any]) -> str:
    """分析主体的确定性身份：body_hash 前 24 位（与 run_id 风格一致）。"""
    return stable_hash(body)[:24]


def seal_analysis(output_dir: str | Path, body: Mapping[str, Any]) -> dict[str, Any]:
    """把分析主体封存为只追加报告并延长哈希链；幂等且永不覆盖历史。

    返回封皮（含 body_hash、analysis_id、chain_hash、sealed_at 与文件路径）。
    """
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    body_hash = stable_hash(body)
    analysis_id = body_hash[:24]
    report_path = root / f"analysis-{analysis_id}.json"

    index_path = root / INDEX_NAME
    index = _load_index(index_path)
    previous_chain = index[-1]["chain_hash"] if index else GENESIS_HASH
    chain_hash = stable_hash({"previous_chain": previous_chain, "body_hash": body_hash})

    envelope = {
        "analysis_id": analysis_id,
        "body_hash": body_hash,
        "chain_hash": chain_hash,
        "previous_chain": previous_chain,
        "sealed_at": utc_now(),
        "analysis_version": ANALYSIS_VERSION,
        "body": body,
    }

    if report_path.exists():
        existing = json.loads(report_path.read_text(encoding="utf-8"))
        if existing.get("body_hash") != body_hash:
            raise FileExistsError(
                f"sealed report path collision with different content: {report_path}")
        # 同内容重放：报告与链条目均已存在，幂等返回既有封皮。
        if any(entry["analysis_id"] == analysis_id for entry in index):
            return existing
    else:
        report_path.write_text(
            json.dumps(envelope, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8")

    if not any(entry["analysis_id"] == analysis_id for entry in index):
        index.append({
            "analysis_id": analysis_id,
            "body_hash": body_hash,
            "chain_hash": chain_hash,
            "previous_chain": previous_chain,
            "sealed_at": envelope["sealed_at"],
            "report_file": report_path.name,
        })
        _write_index(index_path, index)
    return envelope


def verify_sealed_analysis(output_dir: str | Path, analysis_id: str,
                          repository: Any | None = None) -> dict[str, Any]:
    """核验单个封存报告：文件哈希、链位置，以及（可选）对原始记录/决定的回链。"""
    root = Path(output_dir)
    report_path = root / f"analysis-{analysis_id}.json"
    errors: list[str] = []
    if not report_path.is_file():
        return {"ok": False, "analysis_id": analysis_id,
                "errors": [f"report missing: {report_path.name}"]}

    envelope = json.loads(report_path.read_text(encoding="utf-8"))
    body = envelope.get("body")
    if not isinstance(body, dict):
        errors.append("report body is missing or invalid")
        return {"ok": False, "analysis_id": analysis_id, "errors": errors}

    recomputed_body_hash = stable_hash(body)
    if envelope.get("body_hash") != recomputed_body_hash:
        errors.append("body_hash mismatch against recomputed body")
    if envelope.get("analysis_id") != recomputed_body_hash[:24]:
        errors.append("analysis_id mismatch against body hash")

    index = _load_index(root / INDEX_NAME)
    entries = [entry for entry in index if entry.get("analysis_id") == analysis_id]
    if not entries:
        errors.append("analysis not found in hash chain index")
    else:
        entry = entries[0]
        expected_chain = stable_hash(
            {"previous_chain": entry["previous_chain"], "body_hash": recomputed_body_hash})
        if entry.get("chain_hash") != expected_chain:
            errors.append("index chain_hash mismatch")
        if entry.get("body_hash") != recomputed_body_hash:
            errors.append("index body_hash mismatch")

    chain_errors = verify_analysis_index(output_dir)
    errors.extend(chain_errors)

    if repository is not None:
        errors.extend(_verify_traceability(body, repository))

    return {"ok": not errors, "analysis_id": analysis_id,
            "body_hash": recomputed_body_hash, "errors": errors}


def verify_analysis_index(output_dir: str | Path) -> list[str]:
    """核验整份追加索引的哈希链完整性（检测插入、删除、改写）。"""
    index_path = Path(output_dir) / INDEX_NAME
    if not index_path.is_file():
        return [f"{INDEX_NAME} is missing"]
    index = _load_index(index_path)
    errors: list[str] = []
    previous = GENESIS_HASH
    seen: set[str] = set()
    for position, entry in enumerate(index):
        if entry.get("analysis_id") in seen:
            errors.append(f"duplicate analysis_id at position {position}")
        seen.add(entry.get("analysis_id", ""))
        expected = stable_hash(
            {"previous_chain": previous, "body_hash": entry.get("body_hash")})
        if entry.get("previous_chain") != previous:
            errors.append(f"index entry {position} previous_chain mismatch")
        if entry.get("chain_hash") != expected:
            errors.append(f"index entry {position} chain_hash mismatch")
        report_path = Path(output_dir) / entry.get("report_file", "")
        if not report_path.is_file():
            errors.append(f"index entry {position} report file missing")
        previous = entry.get("chain_hash", previous)
    return errors


def _verify_traceability(body: Mapping[str, Any], repository: Any) -> list[str]:
    """把报告回链逐项核对到封存库中的原始记录版本与决定。"""
    errors: list[str] = []
    traceability = body.get("traceability", {})
    for record_id, ref in traceability.get("record_refs", {}).items():
        stored = repository.get_record(record_id)
        if stored is None:
            errors.append(f"traceability: record {record_id} absent from repository")
            continue
        if stored.fingerprint != ref.get("fingerprint"):
            errors.append(
                f"traceability: record {record_id} fingerprint diverges from sealed body "
                "(a later amendment changed the record)")
        if stored.version != ref.get("version"):
            errors.append(
                f"traceability: record {record_id} version {stored.version} != sealed "
                f"version {ref.get('version')}")
    decision_rows = {row["record_id"]: row for row in repository.decision_rows()}
    for record_id, ref in traceability.get("decision_refs", {}).items():
        row = decision_rows.get(record_id)
        if row is None:
            errors.append(f"traceability: decision for {record_id} absent from repository")
            continue
        if stable_hash(row) != ref.get("decision_id"):
            errors.append(
                f"traceability: decision {record_id} fingerprint diverges from sealed body")
    return errors


def _load_index(index_path: Path) -> list[dict[str, Any]]:
    if not index_path.is_file():
        return []
    return json.loads(index_path.read_text(encoding="utf-8"))


def _write_index(index_path: Path, index: Sequence[Mapping[str, Any]]) -> None:
    index_path.write_text(
        json.dumps(list(index), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")


def list_sealed_analyses(output_dir: str | Path) -> list[dict[str, Any]]:
    """按链顺序列出已封存分析（不含正文，仅元数据）。"""
    return _load_index(Path(output_dir) / INDEX_NAME)
