from __future__ import annotations

import unittest
from consensus_workbench.agenda.item_contract import DomainRecord
from consensus_workbench.evidence.evidence_match import match, agenda_board_pressure, shortlist


class MatchingTests(unittest.TestCase):
    def record(self, key):
        return DomainRecord(key, {"working_group": "manufacturing", "issue_urgency": 8, "evidence_maturity": 0.8,
            "deliberation_window": 90, "resource_band": 7, "risk_class": 2, "regional_relevance": 0.6,
            "dependency_count": 4, "expert_capacity": 0.7, "evidence_strength": 0.8,
            "conflict_count": 1, "public_value": 0.9})

    def test_shortlist_prefers_independent_evidence(self):
        record = self.record("d1")
        suppliers = {"good": {"capacity": .9, "evidence": .9, "independence": .9},
                     "weak": {"capacity": .2, "evidence": .3, "independence": .1}}
        self.assertEqual(shortlist(record, suppliers, 1)[0].supplier_id, "good")
        self.assertGreater(match(record, "good", suppliers["good"]).fit, match(record, "weak", suppliers["weak"]).fit)

    def test_agenda_board_pressure_tracks_diversity(self):
        self.assertGreater(agenda_board_pressure([self.record("a"), self.record("b")])["capacity_mean"], 0.0)
