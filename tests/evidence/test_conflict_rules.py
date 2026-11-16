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

class RuleGroup2Tests(unittest.TestCase):
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

    def test_check_deliberation_window_presence_02_01(self):
        record = make_record(4)
        result = RULE_INDEX['check_deliberation_window_presence'](record, {'check_deliberation_window_presence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_range_02_02(self):
        record = make_record(5)
        result = RULE_INDEX['check_deliberation_window_range'](record, {'check_deliberation_window_range_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_stability_02_03(self):
        record = make_record(6)
        result = RULE_INDEX['check_deliberation_window_stability'](record, {'check_deliberation_window_stability_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_freshness_02_04(self):
        record = make_record(7)
        result = RULE_INDEX['check_deliberation_window_freshness'](record, {'check_deliberation_window_freshness_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_coverage_02_05(self):
        record = make_record(8)
        result = RULE_INDEX['check_deliberation_window_coverage'](record, {'check_deliberation_window_coverage_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_consistency_02_06(self):
        record = make_record(9)
        result = RULE_INDEX['check_deliberation_window_consistency'](record, {'check_deliberation_window_consistency_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_risk_02_07(self):
        record = make_record(10)
        result = RULE_INDEX['check_deliberation_window_risk'](record, {'check_deliberation_window_risk_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_confidence_02_08(self):
        record = make_record(11)
        result = RULE_INDEX['check_deliberation_window_confidence'](record, {'check_deliberation_window_confidence_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_dependency_02_09(self):
        record = make_record(12)
        result = RULE_INDEX['check_deliberation_window_dependency'](record, {'check_deliberation_window_dependency_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_deliberation_window_readiness_02_10(self):
        record = make_record(13)
        result = RULE_INDEX['check_deliberation_window_readiness'](record, {'check_deliberation_window_readiness_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_deliberation_window_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_presence_02_11(self):
        record = make_record(14)
        result = RULE_INDEX['check_resource_band_presence'](record, {'check_resource_band_presence_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_range_02_12(self):
        record = make_record(15)
        result = RULE_INDEX['check_resource_band_range'](record, {'check_resource_band_range_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_stability_02_13(self):
        record = make_record(16)
        result = RULE_INDEX['check_resource_band_stability'](record, {'check_resource_band_stability_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_freshness_02_14(self):
        record = make_record(17)
        result = RULE_INDEX['check_resource_band_freshness'](record, {'check_resource_band_freshness_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_coverage_02_15(self):
        record = make_record(18)
        result = RULE_INDEX['check_resource_band_coverage'](record, {'check_resource_band_coverage_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_consistency_02_16(self):
        record = make_record(19)
        result = RULE_INDEX['check_resource_band_consistency'](record, {'check_resource_band_consistency_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_risk_02_17(self):
        record = make_record(20)
        result = RULE_INDEX['check_resource_band_risk'](record, {'check_resource_band_risk_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_confidence_02_18(self):
        record = make_record(21)
        result = RULE_INDEX['check_resource_band_confidence'](record, {'check_resource_band_confidence_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_dependency_02_19(self):
        record = make_record(22)
        result = RULE_INDEX['check_resource_band_dependency'](record, {'check_resource_band_dependency_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_resource_band_readiness_02_20(self):
        record = make_record(23)
        result = RULE_INDEX['check_resource_band_readiness'](record, {'check_resource_band_readiness_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_resource_band_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_presence_02_21(self):
        record = make_record(24)
        result = RULE_INDEX['check_risk_class_presence'](record, {'check_risk_class_presence_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_range_02_22(self):
        record = make_record(25)
        result = RULE_INDEX['check_risk_class_range'](record, {'check_risk_class_range_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_stability_02_23(self):
        record = make_record(26)
        result = RULE_INDEX['check_risk_class_stability'](record, {'check_risk_class_stability_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_freshness_02_24(self):
        record = make_record(27)
        result = RULE_INDEX['check_risk_class_freshness'](record, {'check_risk_class_freshness_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_coverage_02_25(self):
        record = make_record(28)
        result = RULE_INDEX['check_risk_class_coverage'](record, {'check_risk_class_coverage_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_consistency_02_26(self):
        record = make_record(29)
        result = RULE_INDEX['check_risk_class_consistency'](record, {'check_risk_class_consistency_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_risk_02_27(self):
        record = make_record(30)
        result = RULE_INDEX['check_risk_class_risk'](record, {'check_risk_class_risk_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_confidence_02_28(self):
        record = make_record(31)
        result = RULE_INDEX['check_risk_class_confidence'](record, {'check_risk_class_confidence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_dependency_02_29(self):
        record = make_record(32)
        result = RULE_INDEX['check_risk_class_dependency'](record, {'check_risk_class_dependency_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_risk_class_readiness_02_30(self):
        record = make_record(33)
        result = RULE_INDEX['check_risk_class_readiness'](record, {'check_risk_class_readiness_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_risk_class_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

class MetricGroup2Tests(unittest.TestCase):
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
