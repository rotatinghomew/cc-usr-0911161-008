from __future__ import annotations
import unittest
from consensus_workbench.consensus_signal.consensus_readiness import consensus_readiness, peer_distribution
class Record:
    def __init__(self, payload): self.payload = payload
class SignalTests(unittest.TestCase):
    def setUp(self): self.payload = {'working_group': 'safety', 'issue_urgency': 75, 'evidence_maturity': 0.78, 'deliberation_window': 30, 'resource_band': 2, 'risk_class': 2, 'regional_relevance': 0.85, 'dependency_count': 3, 'expert_capacity': 18, 'evidence_strength': 0.82, 'conflict_count': 2, 'public_value': 0.9}
    def test_signal_is_bounded_and_explainable(self):
        signal = consensus_readiness(self.payload)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)
        self.assertIn(signal.severity, {'info', 'warning', 'critical'})
        self.assertTrue({'conflicts', 'quorum_margin', 'dependency_fit'}.issubset(signal.evidence))
    def test_peer_distribution_uses_business_group(self):
        other = dict(self.payload); other['working_group'] = 'group-b'
        result = peer_distribution([Record(self.payload), Record(other)])
        self.assertEqual(result['count'], 2)
        self.assertIn('working_groups', result)
    def test_material_business_change_is_observable(self):
        changed = dict(self.payload); changed['conflict_count'] = 20
        self.assertNotEqual(consensus_readiness(changed).score, consensus_readiness(self.payload).score)
    def test_business_variant_1(self):
        changed = dict(self.payload)
        changed['evidence_maturity'] = self.payload['evidence_maturity']
        signal = consensus_readiness(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_2(self):
        changed = dict(self.payload)
        changed['deliberation_window'] = self.payload['deliberation_window']
        signal = consensus_readiness(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_3(self):
        changed = dict(self.payload)
        changed['resource_band'] = self.payload['resource_band']
        signal = consensus_readiness(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_4(self):
        changed = dict(self.payload)
        changed['risk_class'] = self.payload['risk_class']
        signal = consensus_readiness(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_5(self):
        changed = dict(self.payload)
        changed['regional_relevance'] = self.payload['regional_relevance']
        signal = consensus_readiness(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_6(self):
        changed = dict(self.payload)
        changed['dependency_count'] = self.payload['dependency_count']
        signal = consensus_readiness(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

if __name__ == '__main__': unittest.main()
