from __future__ import annotations

import json
import unittest
from pathlib import Path

from consensus_workbench.agenda.item_contract import records_from_fixture
from consensus_workbench.ballots.vote_governance import decide
from consensus_workbench.grouping.evidence_groups import build_group_report
from consensus_workbench.grouping.influence_analysis import (
    build_influence_report,
    counterfactual_without_duplicates,
    replay_decisions,
)

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "acceptance.json"


def load_records():
    return records_from_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))


class ReplayTests(unittest.TestCase):
    @staticmethod
    def _content(decision):
        # decided_at 是封存时刻，不参与可复算内容；只比较决定本体。
        body = decision.as_dict()
        body.pop("decided_at", None)
        return body

    def test_replay_uses_full_production_context(self):
        from consensus_workbench.evidence.evidence_match import derive_context
        from consensus_workbench.consensus_signal.consensus_readiness import augment_context
        records = load_records()
        replayed = replay_decisions(records)
        self.assertEqual(set(replayed), {record.record_id for record in records})
        # 用与生产 process() 相同的上下文手工决定首条记录，必须与重放一致；
        # 独立 decide(record) 使用空上下文，结果不同正是预期（上下文含议程板压力）。
        first = records[0]
        repo = type("Repo", (), {"list_records": lambda self, state=None: records})()
        context = {}
        context.update(derive_context(first, repo))
        context.update(augment_context(first, repo))
        self.assertEqual(self._content(replayed[first.record_id]),
                         self._content(decide(first, context)))

    def test_replay_is_read_only_and_deterministic(self):
        records = load_records()
        first = replay_decisions(records)
        second = replay_decisions(records)
        self.assertEqual({k: self._content(v) for k, v in first.items()},
                         {k: self._content(v) for k, v in second.items()})


class InfluenceReportTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()
        self.body = build_group_report(self.records)
        self.baseline = replay_decisions(self.records)
        self.report = build_influence_report(self.body, self.records, self.baseline)

    def test_every_present_and_absent_group_is_judged(self):
        judged = {entry["working_group"] for entry in self.report["group_influence"]}
        self.assertEqual(judged, {f"working_group-{i}" for i in range(8)})

    def test_capacity_critical_groups_affect_advancement(self):
        affecting = set(self.report["groups_affecting_advancement"])
        self.assertEqual(affecting,
                         {"working_group-0", "working_group-1", "working_group-2",
                          "working_group-3", "working_group-4"})
        for entry in self.report["group_influence"]:
            if entry["present"]:
                self.assertIn("decision_critical", entry["influence_categories"])
                self.assertTrue(entry["affects_advancement"])
                self.assertEqual(entry["held_member_count"], len(entry["member_decisions"]))

    def test_hidden_readiness_blocks_are_named_not_averaged_away(self):
        self.assertEqual(set(self.report["groups_readiness_blocked_hidden"]),
                         {"working_group-0", "working_group-1", "working_group-2"})

    def test_duplicate_inflation_is_attributed_to_involved_groups(self):
        self.assertEqual(self.report["groups_with_duplicate_inflation"],
                         ["working_group-2"])

    def test_absent_groups_are_unassessable_not_counted_as_support(self):
        absent_entries = [entry for entry in self.report["group_influence"]
                          if not entry["present"]]
        self.assertEqual({entry["working_group"] for entry in absent_entries},
                         {"working_group-5", "working_group-6", "working_group-7"})
        for entry in absent_entries:
            self.assertEqual(entry["influence_categories"], ["unassessable_absent"])
            self.assertFalse(entry["affects_advancement"])

    def test_counterfactual_dedup_removes_only_duplicate_role(self):
        result = self._counterfactual()
        self.assertEqual(result.removed_duplicate_records, ("agenda_item-008",))
        self.assertEqual(len(result.retained_records), 7)
        self.assertNotIn("agenda_item-008", result.counterfactual_outcomes)
        # 本批数据中重复证据虚增信号但未改变任何封存决定，结论必须显式说明。
        self.assertFalse(result.any_outcome_changed)
        self.assertIn("unchanged", self.report["counterfactual_interpretation"])

    def _counterfactual(self):
        from consensus_workbench.grouping.evidence_groups import ClassifiedRecord
        classified = [ClassifiedRecord.from_dict(item) for item in self.body["records"]]
        return counterfactual_without_duplicates(self.records, classified, self.baseline)

    def test_each_member_decision_carries_fingerprint_for_audit(self):
        for entry in self.report["group_influence"]:
            for record_id, brief in entry["member_decisions"].items():
                self.assertEqual(len(brief["decision_id"]), 64)
                self.assertIn(brief["outcome"], {"approve", "review", "reject", "hold"})


if __name__ == "__main__":
    unittest.main()
