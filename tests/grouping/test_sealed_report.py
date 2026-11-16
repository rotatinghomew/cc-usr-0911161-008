from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from consensus_workbench.agenda.item_contract import records_from_fixture
from consensus_workbench.grouping.influence_analysis import replay_decisions
from consensus_workbench.grouping.sealed_report import (
    INDEX_NAME,
    analysis_identity,
    build_analysis,
    list_sealed_analyses,
    seal_analysis,
    verify_analysis_index,
    verify_sealed_analysis,
)
from consensus_workbench.records.deliberation_store import Repository
from consensus_workbench.secretariat import Application, analyze, run, verify

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "acceptance.json"
FIXTURE_HASH_FILE = FIXTURE


def load_records():
    return records_from_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))


class SealedReportTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()
        self.decisions = replay_decisions(self.records)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.analysis_dir = Path(self.temp.name) / "analysis"

    def _body(self):
        return build_analysis(self.records, self.decisions,
                              fixture_hash="a" * 64, run_id="run-001")

    def test_body_hash_is_deterministic_and_excludes_timestamps(self):
        first = build_analysis(self.records, self.decisions, "a" * 64, "run-001")
        second = build_analysis(self.records, self.decisions, "a" * 64, "run-001")
        self.assertEqual(analysis_identity(first), analysis_identity(second))

    def test_seal_is_idempotent_and_extends_chain_once(self):
        body = self._body()
        first = seal_analysis(self.analysis_dir, body)
        second = seal_analysis(self.analysis_dir, body)
        self.assertEqual(first["analysis_id"], second["analysis_id"])
        self.assertEqual(first["chain_hash"], second["chain_hash"])
        index = list_sealed_analyses(self.analysis_dir)
        self.assertEqual(len(index), 1)
        self.assertTrue((self.analysis_dir /
                         f"analysis-{first['analysis_id']}.json").is_file())

    def test_distinct_inputs_append_distinct_reports_and_chain_links(self):
        body_one = build_analysis(self.records, self.decisions, "a" * 64, "run-001")
        body_two = build_analysis(self.records, self.decisions, "b" * 64, "run-002")
        seal_one = seal_analysis(self.analysis_dir, body_one)
        seal_two = seal_analysis(self.analysis_dir, body_two)
        self.assertNotEqual(seal_one["analysis_id"], seal_two["analysis_id"])
        index = list_sealed_analyses(self.analysis_dir)
        self.assertEqual(len(index), 2)
        self.assertEqual(index[1]["previous_chain"], index[0]["chain_hash"])
        self.assertEqual(verify_analysis_index(self.analysis_dir), [])

    def test_verify_reports_body_tampering(self):
        envelope = seal_analysis(self.analysis_dir, self._body())
        report_path = self.analysis_dir / f"analysis-{envelope['analysis_id']}.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["body"]["group_consensus"]["absent_groups"] = ["working_group-9"]
        report_path.write_text(json.dumps(report), encoding="utf-8")
        result = verify_sealed_analysis(self.analysis_dir, envelope["analysis_id"])
        self.assertFalse(result["ok"])
        self.assertTrue(any("body_hash mismatch" in error for error in result["errors"]))

    def test_verify_detects_chain_rewrite(self):
        envelope = seal_analysis(self.analysis_dir, self._body())
        index_path = self.analysis_dir / INDEX_NAME
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index[0]["body_hash"] = "f" * 64
        index_path.write_text(json.dumps(index), encoding="utf-8")
        errors = verify_analysis_index(self.analysis_dir)
        self.assertTrue(any("chain_hash mismatch" in error for error in errors))
        result = verify_sealed_analysis(self.analysis_dir, envelope["analysis_id"])
        self.assertFalse(result["ok"])

    def test_traceability_checks_record_fingerprints_against_repository(self):
        envelope = seal_analysis(self.analysis_dir, self._body())
        temp_db = Path(self.temp.name) / "state.sqlite3"
        repository = Repository(temp_db)
        for record in self.records:
            repository.save_record(record)
        ok_repo = verify_sealed_analysis(self.analysis_dir, envelope["analysis_id"],
                                         repository)
        # 决定尚未入库 -> 回链核验必须报缺失，而不是静默通过。
        self.assertFalse(ok_repo["ok"])
        self.assertTrue(any("decision" in error for error in ok_repo["errors"]))


class ApplicationSealTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "state.sqlite3"
        self.output = self.root / "output"
        self.analysis_dir = self.root / "analysis"

    def test_analyze_requires_a_sealed_run(self):
        with self.assertRaisesRegex(Exception, "sealed run"):
            Application(self.database).analyze(self.analysis_dir)

    def test_end_to_end_seal_verify_and_backfill_immutability(self):
        run(FIXTURE, self.database, self.output)
        sealed = analyze(self.database, self.analysis_dir)
        self.assertEqual(sealed["sealed_analyses"], 1)

        verified = verify(self.database, self.output, self.analysis_dir)
        self.assertTrue(verified["ok"], verified)
        self.assertEqual(verified["analysis_errors"], [])

        # 同一封存状态重复分析：幂等，不产生第二份报告。
        again = analyze(self.database, self.analysis_dir)
        self.assertEqual(again["analysis_id"], sealed["analysis_id"])
        self.assertEqual(len(list_sealed_analyses(self.analysis_dir)), 1)

        # 补录：对一条记录做有效修订并重新跑一轮（新版本、新决定、新 run）。
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        amended = json.loads(json.dumps(fixture))
        amended["records"][0]["payload"]["conflict_count"] = 5.0
        amended_path = self.root / "amended.json"
        amended_path.write_text(json.dumps(amended), encoding="utf-8")
        run(amended_path, self.database, self.output)
        after = analyze(self.database, self.analysis_dir)

        # 新分析被追加；旧报告文件与旧结论原样保留，链上可独立核验。
        self.assertNotEqual(after["analysis_id"], sealed["analysis_id"])
        index = list_sealed_analyses(self.analysis_dir)
        self.assertEqual(len(index), 2)
        old_report = self.analysis_dir / f"analysis-{sealed['analysis_id']}.json"
        old_body = json.loads(old_report.read_text(encoding="utf-8"))["body"]
        self.assertEqual(
            old_body["group_consensus"]["records"][0]["record_id"],
            "agenda_item-001")
        self.assertEqual(
            old_body["traceability"]["record_refs"]["agenda_item-001"]["version"], 2)
        self.assertEqual(verify_analysis_index(self.analysis_dir), [])

        # 旧报告回链指向修订前的指纹；与当前库记录核对时必须显式报分歧，
        # 证明补录没有让旧结论无声改变。
        old_check = verify_sealed_analysis(
            self.analysis_dir, sealed["analysis_id"], Repository(self.database))
        self.assertFalse(old_check["ok"])
        self.assertTrue(any("agenda_item-001" in error and "diverges" in error
                            for error in old_check["errors"]))

        # 最新报告与当前库一致，整体 verify 仍通过。
        fresh_check = verify_sealed_analysis(
            self.analysis_dir, after["analysis_id"], Repository(self.database))
        self.assertTrue(fresh_check["ok"], fresh_check["errors"])


if __name__ == "__main__":
    unittest.main()
