from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from consensus_workbench.agenda.item_contract import ContractError, DomainRecord, RuleResult, bounded, stable_hash
from consensus_workbench.evidence.conflict_rules import RULE_INDEX, evaluate, summarize
from consensus_workbench.agenda_board.portfolio_selection import METRICS, compare, grouped_metrics, metric_vector, agenda_board, record_score

FIELDS = ['working_group', 'issue_urgency', 'evidence_maturity', 'deliberation_window', 'resource_band', 'risk_class', 'regional_relevance', 'dependency_count', 'expert_capacity', 'evidence_strength', 'conflict_count', 'public_value']

def make_record(seed: int = 1, state: str | None = None) -> DomainRecord:
    payload = {}
    for index, field in enumerate(FIELDS):
        selector = (seed + index) % 4
        if selector == 0:
            payload[field] = seed * 9.5 + index * 1.25
        elif selector == 1:
            payload[field] = f'{field}-{seed % 5}'
        elif selector == 2:
            payload[field] = (seed + index) / 10.0
        else:
            payload[field] = (seed + index) % 2 == 0
    return DomainRecord(f'agenda_item-{seed:03d}', payload, state or 'submitted')

class RuleGroup3Tests(unittest.TestCase):
    def test_evaluate_returns_complete_catalog(self):
        record = make_record()
        results = evaluate(record, {})
        self.assertEqual(len(results), len(RULE_INDEX))
        self.assertTrue(all(isinstance(item, RuleResult) for item in results))
        self.assertTrue(all(0.0 <= item.score <= 1.0 for item in results))

    def test_summary_is_conservative_and_counted(self):
        results = evaluate(make_record(2), {'risk_weight': 0.8})
        summary = summarize(results)
        self.assertEqual(summary['passed'] + summary['failed'], len(results))
        self.assertGreaterEqual(summary['critical'], 0)
        self.assertGreaterEqual(summary['score'], 0.0)
        self.assertLessEqual(summary['score'], 1.0)

    def test_check_regional_relevance_presence_03_01(self):
        record = make_record(5)
        result = RULE_INDEX['check_regional_relevance_presence'](record, {'check_regional_relevance_presence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_range_03_02(self):
        record = make_record(6)
        result = RULE_INDEX['check_regional_relevance_range'](record, {'check_regional_relevance_range_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_stability_03_03(self):
        record = make_record(7)
        result = RULE_INDEX['check_regional_relevance_stability'](record, {'check_regional_relevance_stability_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_freshness_03_04(self):
        record = make_record(8)
        result = RULE_INDEX['check_regional_relevance_freshness'](record, {'check_regional_relevance_freshness_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_coverage_03_05(self):
        record = make_record(9)
        result = RULE_INDEX['check_regional_relevance_coverage'](record, {'check_regional_relevance_coverage_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_consistency_03_06(self):
        record = make_record(10)
        result = RULE_INDEX['check_regional_relevance_consistency'](record, {'check_regional_relevance_consistency_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_risk_03_07(self):
        record = make_record(11)
        result = RULE_INDEX['check_regional_relevance_risk'](record, {'check_regional_relevance_risk_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_confidence_03_08(self):
        record = make_record(12)
        result = RULE_INDEX['check_regional_relevance_confidence'](record, {'check_regional_relevance_confidence_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_dependency_03_09(self):
        record = make_record(13)
        result = RULE_INDEX['check_regional_relevance_dependency'](record, {'check_regional_relevance_dependency_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_regional_relevance_readiness_03_10(self):
        record = make_record(14)
        result = RULE_INDEX['check_regional_relevance_readiness'](record, {'check_regional_relevance_readiness_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_regional_relevance_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_presence_03_11(self):
        record = make_record(15)
        result = RULE_INDEX['check_dependency_count_presence'](record, {'check_dependency_count_presence_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_range_03_12(self):
        record = make_record(16)
        result = RULE_INDEX['check_dependency_count_range'](record, {'check_dependency_count_range_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_stability_03_13(self):
        record = make_record(17)
        result = RULE_INDEX['check_dependency_count_stability'](record, {'check_dependency_count_stability_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_freshness_03_14(self):
        record = make_record(18)
        result = RULE_INDEX['check_dependency_count_freshness'](record, {'check_dependency_count_freshness_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_coverage_03_15(self):
        record = make_record(19)
        result = RULE_INDEX['check_dependency_count_coverage'](record, {'check_dependency_count_coverage_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_consistency_03_16(self):
        record = make_record(20)
        result = RULE_INDEX['check_dependency_count_consistency'](record, {'check_dependency_count_consistency_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_risk_03_17(self):
        record = make_record(21)
        result = RULE_INDEX['check_dependency_count_risk'](record, {'check_dependency_count_risk_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_confidence_03_18(self):
        record = make_record(22)
        result = RULE_INDEX['check_dependency_count_confidence'](record, {'check_dependency_count_confidence_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_dependency_03_19(self):
        record = make_record(23)
        result = RULE_INDEX['check_dependency_count_dependency'](record, {'check_dependency_count_dependency_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_dependency_count_readiness_03_20(self):
        record = make_record(24)
        result = RULE_INDEX['check_dependency_count_readiness'](record, {'check_dependency_count_readiness_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_dependency_count_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_presence_03_21(self):
        record = make_record(25)
        result = RULE_INDEX['check_expert_capacity_presence'](record, {'check_expert_capacity_presence_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_range_03_22(self):
        record = make_record(26)
        result = RULE_INDEX['check_expert_capacity_range'](record, {'check_expert_capacity_range_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_stability_03_23(self):
        record = make_record(27)
        result = RULE_INDEX['check_expert_capacity_stability'](record, {'check_expert_capacity_stability_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_freshness_03_24(self):
        record = make_record(28)
        result = RULE_INDEX['check_expert_capacity_freshness'](record, {'check_expert_capacity_freshness_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_coverage_03_25(self):
        record = make_record(29)
        result = RULE_INDEX['check_expert_capacity_coverage'](record, {'check_expert_capacity_coverage_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_consistency_03_26(self):
        record = make_record(30)
        result = RULE_INDEX['check_expert_capacity_consistency'](record, {'check_expert_capacity_consistency_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_risk_03_27(self):
        record = make_record(31)
        result = RULE_INDEX['check_expert_capacity_risk'](record, {'check_expert_capacity_risk_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_confidence_03_28(self):
        record = make_record(32)
        result = RULE_INDEX['check_expert_capacity_confidence'](record, {'check_expert_capacity_confidence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_dependency_03_29(self):
        record = make_record(33)
        result = RULE_INDEX['check_expert_capacity_dependency'](record, {'check_expert_capacity_dependency_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_expert_capacity_readiness_03_30(self):
        record = make_record(34)
        result = RULE_INDEX['check_expert_capacity_readiness'](record, {'check_expert_capacity_readiness_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_expert_capacity_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

class MetricGroup3Tests(unittest.TestCase):
    def test_metric_vector_is_deterministic(self):
        record = make_record(11)
        first = metric_vector(record, {})
        second = metric_vector(record, {})
        self.assertEqual(first, second)
        self.assertEqual(set(first), set(METRICS))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in first.values()))

    def test_grouped_metrics_match_business_catalog(self):
        grouped = grouped_metrics(make_record(4), {})
        self.assertEqual(set(grouped), {'agenda_board_balance', 'disclosure_quality', 'exit_risk', 'benefit_confidence', 'match_fit', 'evidence_velocity', 'pilot_feasibility', 'supplier_concentration'})
        self.assertTrue(all(math.isfinite(value) for value in grouped.values()))

    def test_agenda_board_orders_by_descending_score(self):
        result = agenda_board([make_record(2), make_record(3), make_record(4)])
        scores = [row['score'] for row in result['rows']]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result['count'], 3)
        self.assertGreaterEqual(result['maximum'], result['minimum'])

    def test_compare_has_all_metric_deltas(self):
        result = compare(make_record(5), make_record(6))
        self.assertEqual(set(result['delta']), {'agenda_board_balance', 'disclosure_quality', 'exit_risk', 'benefit_confidence', 'match_fit', 'evidence_velocity', 'pilot_feasibility', 'supplier_concentration'})
        self.assertIn(result['winner'], {make_record(5).record_id, make_record(6).record_id})

    def test_score_fingerprint_changes_with_payload(self):
        left = record_score(make_record(7))
        right = record_score(make_record(8))
        self.assertNotEqual(left['fingerprint'], right['fingerprint'])
        self.assertNotEqual(stable_hash(left['metrics']), stable_hash(right['metrics']))

if __name__ == '__main__':
    unittest.main()
