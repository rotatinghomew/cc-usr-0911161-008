from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from consensus_workbench.agenda.item_contract import records_from_fixture
from consensus_workbench.grouping.evidence_groups import (
    DEFAULT_ROSTER_SIZE,
    READINESS_BLOCK_FLOOR,
    build_group_report,
    classify_records,
    evidence_signature,
    expected_roster,
)

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "acceptance.json"


def load_records():
    return records_from_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))


class EvidenceSignatureTests(unittest.TestCase):
    def test_signature_is_stable_and_field_sensitive(self):
        records = load_records()
        first = evidence_signature(records[0].payload)
        self.assertEqual(first, evidence_signature(records[0].payload))
        self.assertEqual(len(first), 64)
        changed = records[0].with_payload({"evidence_strength": 0.11}).payload
        self.assertNotEqual(first, evidence_signature(changed))

    def test_known_duplicate_pair_shares_signature(self):
        records = {record.record_id: record for record in load_records()}
        self.assertEqual(
            evidence_signature(records["agenda_item-001"].payload),
            evidence_signature(records["agenda_item-008"].payload))


class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()
        self.classified = classify_records(self.records)

    def test_every_record_is_classified_with_traceable_refs(self):
        self.assertEqual(len(self.classified), len(self.records))
        ids = {item.record_id for item in self.classified}
        self.assertEqual(ids, {record.record_id for record in self.records})
        for item in self.classified:
            self.assertTrue(item.fingerprint)
            self.assertGreaterEqual(item.version, 1)
            self.assertIn(item.record_role, {"independent_issue", "duplicate_evidence"})

    def test_duplicate_evidence_is_distinguished_from_independent_issues(self):
        roles = {item.record_id: item.record_role for item in self.classified}
        # 001 是该证据签名的首次出现 -> 独立议题；008 是重复提交。
        self.assertEqual(roles["agenda_item-001"], "independent_issue")
        self.assertEqual(roles["agenda_item-008"], "duplicate_evidence")
        duplicate = next(item for item in self.classified
                         if item.record_id == "agenda_item-008")
        self.assertEqual(duplicate.duplicate_of, ("agenda_item-001",))
        independent = [item for item in self.classified
                       if item.record_role == "independent_issue"]
        duplicates = [item for item in self.classified
                      if item.record_role == "duplicate_evidence"]
        self.assertEqual(len(independent), 7)
        self.assertEqual(len(duplicates), 1)


class GroupReportTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()
        self.report = build_group_report(self.records)

    def test_roster_inference_and_absent_groups(self):
        roster = expected_roster(self.records)
        self.assertEqual(roster, [f"working_group-{i}" for i in range(DEFAULT_ROSTER_SIZE)])
        self.assertEqual(self.report["absent_groups"],
                         ["working_group-5", "working_group-6", "working_group-7"])
        self.assertEqual(self.report["absent_group_count"], 3)
        self.assertEqual(self.report["present_group_count"], 5)

    def test_explicit_roster_override_is_honored(self):
        override = ["alpha", "beta", "gamma"]
        report = build_group_report(self.records, roster_override=override)
        self.assertEqual(report["roster_source"], "override")
        self.assertEqual(report["roster"], override)
        self.assertIn("alpha", report["absent_groups"])

    def test_override_rejects_duplicates(self):
        with self.assertRaises(ValueError):
            build_group_report(self.records, roster_override=["a", "a"])

    def test_group_uses_minimum_not_average_and_flags_hidden_blocks(self):
        groups = {group["working_group"]: group for group in self.report["groups"]}
        blocked = {name for name, group in groups.items()
                   if group["readiness_blocked"]}
        self.assertEqual(blocked, {"working_group-0", "working_group-1", "working_group-2"})
        for group in self.report["groups"]:
            scores = list(group["readiness_scores"].values())
            self.assertEqual(group["readiness_minimum"], min(scores))
            self.assertLess(group["readiness_minimum"],
                            sum(scores) / len(scores) + 1e-12
                            if len(scores) > 1 else float("inf"))

    def test_duplicate_cluster_links_two_working_groups(self):
        clusters = self.report["duplicate_clusters"]
        self.assertEqual(len(clusters), 1)
        cluster = clusters[0]
        self.assertEqual(cluster["record_ids"],
                         ["agenda_item-001", "agenda_item-008"])
        self.assertEqual(cluster["working_groups"],
                         ["working_group-0", "working_group-2"])

    def test_capacity_critical_groups_are_identifiable(self):
        groups = {group["working_group"]: group for group in self.report["groups"]}
        # 全部记录 conflict_count >= expert_capacity，因此每个出席组都应被标记。
        for name in ("working_group-0", "working_group-1", "working_group-2",
                     "working_group-3", "working_group-4"):
            self.assertTrue(groups[name]["capacity_critical_records"])

    def test_report_is_deterministic(self):
        # 记录指纹含 occurred_at 时间戳，故逐字节比较不适用；确定性要求落在
        # 封存判断内容上：剔除回链指纹后，同一输入的分析结论必须稳定。
        from consensus_workbench.agenda.item_contract import stable_hash

        def judgements(report):
            groups = [{key: value for key, value in group.items()
                       if key != "record_refs"} for group in report["groups"]]
            return {key: value for key, value in report.items()
                    if key in ("independent_issue_count", "duplicate_evidence_count",
                               "present_group_count", "absent_group_count", "absent_groups",
                               "readiness_block_floor", "evidence_signature_fields",
                               "duplicate_clusters", "roster", "roster_source")} | {"groups": groups}

        again = build_group_report(load_records())
        self.assertEqual(stable_hash(judgements(self.report)),
                         stable_hash(judgements(again)))


if __name__ == "__main__":
    unittest.main()
