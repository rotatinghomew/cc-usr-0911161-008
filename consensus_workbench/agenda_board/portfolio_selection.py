from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

from consensus_workbench.agenda.item_contract import DomainRecord, bounded, finite_number, normalized_text, stable_hash
from consensus_workbench.evidence.conflict_rules import evaluate, summarize

MetricFunction = Callable[[DomainRecord, Mapping[str, Any]], float]

def _value(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    return float(sum((index + 1) * ord(ch) for index, ch in enumerate(text)) % 997) / 10.0

def _signal(record: DomainRecord, fields: tuple[str, ...], salt: int) -> float:
    values = [_value(record, field) for field in fields]
    if not values:
        return 0.0
    center = statistics.fmean(values)
    spread = statistics.pstdev(values) if len(values) > 1 else 0.0
    harmonic = sum(math.sin(value / (salt + 1)) + math.cos(value * (salt + 1) / 17.0) for value in values)
    return bounded(0.5 + math.tanh((center - spread + harmonic) / (30.0 + salt)) / 2.0)

def metric_match_fit_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('working_group', 'deliberation_window', 'regional_relevance', 'evidence_strength'), 1)
    weight = finite_number(context.get('match_fit_weight', 0.7))
    offset = finite_number(context.get('metric_match_fit_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_match_fit_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('issue_urgency', 'resource_band', 'dependency_count', 'conflict_count'), 2)
    weight = finite_number(context.get('match_fit_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_match_fit_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_match_fit_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_maturity', 'risk_class', 'expert_capacity', 'public_value'), 3)
    weight = finite_number(context.get('match_fit_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_match_fit_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_match_fit_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deliberation_window', 'regional_relevance', 'evidence_strength', 'working_group'), 4)
    weight = finite_number(context.get('match_fit_weight', 1.0))
    offset = finite_number(context.get('metric_match_fit_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_match_fit_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_band', 'dependency_count', 'conflict_count', 'issue_urgency'), 5)
    weight = finite_number(context.get('match_fit_weight', 0.7))
    offset = finite_number(context.get('metric_match_fit_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_match_fit_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_class', 'expert_capacity', 'public_value', 'evidence_maturity'), 6)
    weight = finite_number(context.get('match_fit_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_match_fit_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_match_fit_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('regional_relevance', 'evidence_strength', 'working_group', 'deliberation_window'), 7)
    weight = finite_number(context.get('match_fit_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_match_fit_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_match_fit_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('match_fit_weight', 1.0))
    offset = finite_number(context.get('metric_match_fit_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_match_fit_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('match_fit_weight', 0.7))
    offset = finite_number(context.get('metric_match_fit_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_match_fit_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('match_fit_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_match_fit_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_disclosure_quality_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('issue_urgency', 'resource_band', 'dependency_count', 'conflict_count'), 2)
    weight = finite_number(context.get('disclosure_quality_weight', 0.7))
    offset = finite_number(context.get('metric_disclosure_quality_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_disclosure_quality_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_maturity', 'risk_class', 'expert_capacity', 'public_value'), 3)
    weight = finite_number(context.get('disclosure_quality_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_disclosure_quality_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_disclosure_quality_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deliberation_window', 'regional_relevance', 'evidence_strength', 'working_group'), 4)
    weight = finite_number(context.get('disclosure_quality_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_disclosure_quality_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_disclosure_quality_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_band', 'dependency_count', 'conflict_count', 'issue_urgency'), 5)
    weight = finite_number(context.get('disclosure_quality_weight', 1.0))
    offset = finite_number(context.get('metric_disclosure_quality_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_disclosure_quality_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_class', 'expert_capacity', 'public_value', 'evidence_maturity'), 6)
    weight = finite_number(context.get('disclosure_quality_weight', 0.7))
    offset = finite_number(context.get('metric_disclosure_quality_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_disclosure_quality_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('regional_relevance', 'evidence_strength', 'working_group', 'deliberation_window'), 7)
    weight = finite_number(context.get('disclosure_quality_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_disclosure_quality_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_disclosure_quality_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('disclosure_quality_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_disclosure_quality_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_disclosure_quality_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('disclosure_quality_weight', 1.0))
    offset = finite_number(context.get('metric_disclosure_quality_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_disclosure_quality_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('disclosure_quality_weight', 0.7))
    offset = finite_number(context.get('metric_disclosure_quality_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_disclosure_quality_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('conflict_count', 'issue_urgency', 'resource_band', 'dependency_count'), 11)
    weight = finite_number(context.get('disclosure_quality_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_disclosure_quality_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_maturity', 'risk_class', 'expert_capacity', 'public_value'), 3)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.7))
    offset = finite_number(context.get('metric_pilot_feasibility_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deliberation_window', 'regional_relevance', 'evidence_strength', 'working_group'), 4)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_pilot_feasibility_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_band', 'dependency_count', 'conflict_count', 'issue_urgency'), 5)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_pilot_feasibility_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_class', 'expert_capacity', 'public_value', 'evidence_maturity'), 6)
    weight = finite_number(context.get('pilot_feasibility_weight', 1.0))
    offset = finite_number(context.get('metric_pilot_feasibility_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('regional_relevance', 'evidence_strength', 'working_group', 'deliberation_window'), 7)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.7))
    offset = finite_number(context.get('metric_pilot_feasibility_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_pilot_feasibility_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_pilot_feasibility_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('pilot_feasibility_weight', 1.0))
    offset = finite_number(context.get('metric_pilot_feasibility_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('conflict_count', 'issue_urgency', 'resource_band', 'dependency_count'), 11)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.7))
    offset = finite_number(context.get('metric_pilot_feasibility_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_pilot_feasibility_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value', 'evidence_maturity', 'risk_class', 'expert_capacity'), 12)
    weight = finite_number(context.get('pilot_feasibility_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_pilot_feasibility_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_supplier_concentration_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deliberation_window', 'regional_relevance', 'evidence_strength', 'working_group'), 4)
    weight = finite_number(context.get('supplier_concentration_weight', 0.7))
    offset = finite_number(context.get('metric_supplier_concentration_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_supplier_concentration_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_band', 'dependency_count', 'conflict_count', 'issue_urgency'), 5)
    weight = finite_number(context.get('supplier_concentration_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_supplier_concentration_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_supplier_concentration_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_class', 'expert_capacity', 'public_value', 'evidence_maturity'), 6)
    weight = finite_number(context.get('supplier_concentration_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_supplier_concentration_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_supplier_concentration_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('regional_relevance', 'evidence_strength', 'working_group', 'deliberation_window'), 7)
    weight = finite_number(context.get('supplier_concentration_weight', 1.0))
    offset = finite_number(context.get('metric_supplier_concentration_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_supplier_concentration_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('supplier_concentration_weight', 0.7))
    offset = finite_number(context.get('metric_supplier_concentration_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_supplier_concentration_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('supplier_concentration_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_supplier_concentration_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_supplier_concentration_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('supplier_concentration_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_supplier_concentration_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_supplier_concentration_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('conflict_count', 'issue_urgency', 'resource_band', 'dependency_count'), 11)
    weight = finite_number(context.get('supplier_concentration_weight', 1.0))
    offset = finite_number(context.get('metric_supplier_concentration_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_supplier_concentration_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value', 'evidence_maturity', 'risk_class', 'expert_capacity'), 12)
    weight = finite_number(context.get('supplier_concentration_weight', 0.7))
    offset = finite_number(context.get('metric_supplier_concentration_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_supplier_concentration_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('working_group', 'deliberation_window', 'regional_relevance', 'evidence_strength'), 13)
    weight = finite_number(context.get('supplier_concentration_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_supplier_concentration_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_evidence_velocity_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_band', 'dependency_count', 'conflict_count', 'issue_urgency'), 5)
    weight = finite_number(context.get('evidence_velocity_weight', 0.7))
    offset = finite_number(context.get('metric_evidence_velocity_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_evidence_velocity_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_class', 'expert_capacity', 'public_value', 'evidence_maturity'), 6)
    weight = finite_number(context.get('evidence_velocity_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_evidence_velocity_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_evidence_velocity_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('regional_relevance', 'evidence_strength', 'working_group', 'deliberation_window'), 7)
    weight = finite_number(context.get('evidence_velocity_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_evidence_velocity_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_evidence_velocity_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('evidence_velocity_weight', 1.0))
    offset = finite_number(context.get('metric_evidence_velocity_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_evidence_velocity_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('evidence_velocity_weight', 0.7))
    offset = finite_number(context.get('metric_evidence_velocity_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_evidence_velocity_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('evidence_velocity_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_evidence_velocity_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_evidence_velocity_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('conflict_count', 'issue_urgency', 'resource_band', 'dependency_count'), 11)
    weight = finite_number(context.get('evidence_velocity_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_evidence_velocity_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_evidence_velocity_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value', 'evidence_maturity', 'risk_class', 'expert_capacity'), 12)
    weight = finite_number(context.get('evidence_velocity_weight', 1.0))
    offset = finite_number(context.get('metric_evidence_velocity_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_evidence_velocity_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('working_group', 'deliberation_window', 'regional_relevance', 'evidence_strength'), 13)
    weight = finite_number(context.get('evidence_velocity_weight', 0.7))
    offset = finite_number(context.get('metric_evidence_velocity_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_evidence_velocity_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('issue_urgency', 'resource_band', 'dependency_count', 'conflict_count'), 14)
    weight = finite_number(context.get('evidence_velocity_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_evidence_velocity_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_benefit_confidence_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_class', 'expert_capacity', 'public_value', 'evidence_maturity'), 6)
    weight = finite_number(context.get('benefit_confidence_weight', 0.7))
    offset = finite_number(context.get('metric_benefit_confidence_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_benefit_confidence_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('regional_relevance', 'evidence_strength', 'working_group', 'deliberation_window'), 7)
    weight = finite_number(context.get('benefit_confidence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_benefit_confidence_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_benefit_confidence_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('benefit_confidence_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_benefit_confidence_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_benefit_confidence_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('benefit_confidence_weight', 1.0))
    offset = finite_number(context.get('metric_benefit_confidence_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_benefit_confidence_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('benefit_confidence_weight', 0.7))
    offset = finite_number(context.get('metric_benefit_confidence_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_benefit_confidence_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('conflict_count', 'issue_urgency', 'resource_band', 'dependency_count'), 11)
    weight = finite_number(context.get('benefit_confidence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_benefit_confidence_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_benefit_confidence_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value', 'evidence_maturity', 'risk_class', 'expert_capacity'), 12)
    weight = finite_number(context.get('benefit_confidence_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_benefit_confidence_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_benefit_confidence_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('working_group', 'deliberation_window', 'regional_relevance', 'evidence_strength'), 13)
    weight = finite_number(context.get('benefit_confidence_weight', 1.0))
    offset = finite_number(context.get('metric_benefit_confidence_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_benefit_confidence_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('issue_urgency', 'resource_band', 'dependency_count', 'conflict_count'), 14)
    weight = finite_number(context.get('benefit_confidence_weight', 0.7))
    offset = finite_number(context.get('metric_benefit_confidence_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_benefit_confidence_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_maturity', 'risk_class', 'expert_capacity', 'public_value'), 15)
    weight = finite_number(context.get('benefit_confidence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_benefit_confidence_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_exit_risk_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('regional_relevance', 'evidence_strength', 'working_group', 'deliberation_window'), 7)
    weight = finite_number(context.get('exit_risk_weight', 0.7))
    offset = finite_number(context.get('metric_exit_risk_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_exit_risk_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('exit_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_exit_risk_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_exit_risk_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('exit_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_exit_risk_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_exit_risk_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('exit_risk_weight', 1.0))
    offset = finite_number(context.get('metric_exit_risk_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_exit_risk_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('conflict_count', 'issue_urgency', 'resource_band', 'dependency_count'), 11)
    weight = finite_number(context.get('exit_risk_weight', 0.7))
    offset = finite_number(context.get('metric_exit_risk_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_exit_risk_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value', 'evidence_maturity', 'risk_class', 'expert_capacity'), 12)
    weight = finite_number(context.get('exit_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_exit_risk_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_exit_risk_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('working_group', 'deliberation_window', 'regional_relevance', 'evidence_strength'), 13)
    weight = finite_number(context.get('exit_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_exit_risk_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_exit_risk_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('issue_urgency', 'resource_band', 'dependency_count', 'conflict_count'), 14)
    weight = finite_number(context.get('exit_risk_weight', 1.0))
    offset = finite_number(context.get('metric_exit_risk_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_exit_risk_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_maturity', 'risk_class', 'expert_capacity', 'public_value'), 15)
    weight = finite_number(context.get('exit_risk_weight', 0.7))
    offset = finite_number(context.get('metric_exit_risk_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_exit_risk_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deliberation_window', 'regional_relevance', 'evidence_strength', 'working_group'), 16)
    weight = finite_number(context.get('exit_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_exit_risk_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'conflict_count', 'issue_urgency', 'resource_band'), 8)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.7))
    offset = finite_number(context.get('metric_agenda_board_balance_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('expert_capacity', 'public_value', 'evidence_maturity', 'risk_class'), 9)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_agenda_board_balance_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_strength', 'working_group', 'deliberation_window', 'regional_relevance'), 10)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_agenda_board_balance_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('conflict_count', 'issue_urgency', 'resource_band', 'dependency_count'), 11)
    weight = finite_number(context.get('agenda_board_balance_weight', 1.0))
    offset = finite_number(context.get('metric_agenda_board_balance_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value', 'evidence_maturity', 'risk_class', 'expert_capacity'), 12)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.7))
    offset = finite_number(context.get('metric_agenda_board_balance_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('working_group', 'deliberation_window', 'regional_relevance', 'evidence_strength'), 13)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_agenda_board_balance_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('issue_urgency', 'resource_band', 'dependency_count', 'conflict_count'), 14)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_agenda_board_balance_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_maturity', 'risk_class', 'expert_capacity', 'public_value'), 15)
    weight = finite_number(context.get('agenda_board_balance_weight', 1.0))
    offset = finite_number(context.get('metric_agenda_board_balance_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deliberation_window', 'regional_relevance', 'evidence_strength', 'working_group'), 16)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.7))
    offset = finite_number(context.get('metric_agenda_board_balance_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_agenda_board_balance_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_band', 'dependency_count', 'conflict_count', 'issue_urgency'), 17)
    weight = finite_number(context.get('agenda_board_balance_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_agenda_board_balance_10_offset', 0.1))
    return bounded(base * weight + offset)

METRICS: dict[str, MetricFunction] = {
    'metric_match_fit_01': metric_match_fit_01,
    'metric_match_fit_02': metric_match_fit_02,
    'metric_match_fit_03': metric_match_fit_03,
    'metric_match_fit_04': metric_match_fit_04,
    'metric_match_fit_05': metric_match_fit_05,
    'metric_match_fit_06': metric_match_fit_06,
    'metric_match_fit_07': metric_match_fit_07,
    'metric_match_fit_08': metric_match_fit_08,
    'metric_match_fit_09': metric_match_fit_09,
    'metric_match_fit_10': metric_match_fit_10,
    'metric_disclosure_quality_01': metric_disclosure_quality_01,
    'metric_disclosure_quality_02': metric_disclosure_quality_02,
    'metric_disclosure_quality_03': metric_disclosure_quality_03,
    'metric_disclosure_quality_04': metric_disclosure_quality_04,
    'metric_disclosure_quality_05': metric_disclosure_quality_05,
    'metric_disclosure_quality_06': metric_disclosure_quality_06,
    'metric_disclosure_quality_07': metric_disclosure_quality_07,
    'metric_disclosure_quality_08': metric_disclosure_quality_08,
    'metric_disclosure_quality_09': metric_disclosure_quality_09,
    'metric_disclosure_quality_10': metric_disclosure_quality_10,
    'metric_pilot_feasibility_01': metric_pilot_feasibility_01,
    'metric_pilot_feasibility_02': metric_pilot_feasibility_02,
    'metric_pilot_feasibility_03': metric_pilot_feasibility_03,
    'metric_pilot_feasibility_04': metric_pilot_feasibility_04,
    'metric_pilot_feasibility_05': metric_pilot_feasibility_05,
    'metric_pilot_feasibility_06': metric_pilot_feasibility_06,
    'metric_pilot_feasibility_07': metric_pilot_feasibility_07,
    'metric_pilot_feasibility_08': metric_pilot_feasibility_08,
    'metric_pilot_feasibility_09': metric_pilot_feasibility_09,
    'metric_pilot_feasibility_10': metric_pilot_feasibility_10,
    'metric_supplier_concentration_01': metric_supplier_concentration_01,
    'metric_supplier_concentration_02': metric_supplier_concentration_02,
    'metric_supplier_concentration_03': metric_supplier_concentration_03,
    'metric_supplier_concentration_04': metric_supplier_concentration_04,
    'metric_supplier_concentration_05': metric_supplier_concentration_05,
    'metric_supplier_concentration_06': metric_supplier_concentration_06,
    'metric_supplier_concentration_07': metric_supplier_concentration_07,
    'metric_supplier_concentration_08': metric_supplier_concentration_08,
    'metric_supplier_concentration_09': metric_supplier_concentration_09,
    'metric_supplier_concentration_10': metric_supplier_concentration_10,
    'metric_evidence_velocity_01': metric_evidence_velocity_01,
    'metric_evidence_velocity_02': metric_evidence_velocity_02,
    'metric_evidence_velocity_03': metric_evidence_velocity_03,
    'metric_evidence_velocity_04': metric_evidence_velocity_04,
    'metric_evidence_velocity_05': metric_evidence_velocity_05,
    'metric_evidence_velocity_06': metric_evidence_velocity_06,
    'metric_evidence_velocity_07': metric_evidence_velocity_07,
    'metric_evidence_velocity_08': metric_evidence_velocity_08,
    'metric_evidence_velocity_09': metric_evidence_velocity_09,
    'metric_evidence_velocity_10': metric_evidence_velocity_10,
    'metric_benefit_confidence_01': metric_benefit_confidence_01,
    'metric_benefit_confidence_02': metric_benefit_confidence_02,
    'metric_benefit_confidence_03': metric_benefit_confidence_03,
    'metric_benefit_confidence_04': metric_benefit_confidence_04,
    'metric_benefit_confidence_05': metric_benefit_confidence_05,
    'metric_benefit_confidence_06': metric_benefit_confidence_06,
    'metric_benefit_confidence_07': metric_benefit_confidence_07,
    'metric_benefit_confidence_08': metric_benefit_confidence_08,
    'metric_benefit_confidence_09': metric_benefit_confidence_09,
    'metric_benefit_confidence_10': metric_benefit_confidence_10,
    'metric_exit_risk_01': metric_exit_risk_01,
    'metric_exit_risk_02': metric_exit_risk_02,
    'metric_exit_risk_03': metric_exit_risk_03,
    'metric_exit_risk_04': metric_exit_risk_04,
    'metric_exit_risk_05': metric_exit_risk_05,
    'metric_exit_risk_06': metric_exit_risk_06,
    'metric_exit_risk_07': metric_exit_risk_07,
    'metric_exit_risk_08': metric_exit_risk_08,
    'metric_exit_risk_09': metric_exit_risk_09,
    'metric_exit_risk_10': metric_exit_risk_10,
    'metric_agenda_board_balance_01': metric_agenda_board_balance_01,
    'metric_agenda_board_balance_02': metric_agenda_board_balance_02,
    'metric_agenda_board_balance_03': metric_agenda_board_balance_03,
    'metric_agenda_board_balance_04': metric_agenda_board_balance_04,
    'metric_agenda_board_balance_05': metric_agenda_board_balance_05,
    'metric_agenda_board_balance_06': metric_agenda_board_balance_06,
    'metric_agenda_board_balance_07': metric_agenda_board_balance_07,
    'metric_agenda_board_balance_08': metric_agenda_board_balance_08,
    'metric_agenda_board_balance_09': metric_agenda_board_balance_09,
    'metric_agenda_board_balance_10': metric_agenda_board_balance_10,
}

def metric_vector(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    context = context or {}
    return {name: function(record, context) for name, function in METRICS.items()}

def grouped_metrics(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    vector = metric_vector(record, context)
    groups: dict[str, list[float]] = defaultdict(list)
    for name, value in vector.items():
        key = name.rsplit('_', 1)[0].removeprefix('metric_')
        groups[key].append(value)
    return {key: statistics.fmean(values) for key, values in groups.items()}

def record_score(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    rules = evaluate(record, context)
    rule_summary = summarize(rules)
    metrics = grouped_metrics(record, context)
    metric_score = statistics.fmean(metrics.values()) if metrics else 0.0
    combined = bounded(rule_summary['score'] * 0.55 + metric_score * 0.45)
    return {'score': combined, 'rule_summary': rule_summary, 'metrics': metrics,
            'fingerprint': stable_hash({'record': record.fingerprint, 'metrics': metrics, 'rules': rule_summary})}

def agenda_board(records: Iterable[DomainRecord], context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [record_score(record, context) | {'record_id': record.record_id} for record in records]
    if not rows:
        return {'count': 0, 'average': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'rows': []}
    scores = [row['score'] for row in rows]
    return {'count': len(rows), 'average': statistics.fmean(scores),
            'minimum': min(scores), 'maximum': max(scores), 'rows': sorted(rows, key=lambda row: (-row['score'], row['record_id']))}

def compare(left: DomainRecord, right: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    left_metrics = grouped_metrics(left, context)
    right_metrics = grouped_metrics(right, context)
    delta = {key: right_metrics.get(key, 0.0) - left_metrics.get(key, 0.0) for key in sorted(set(left_metrics) | set(right_metrics))}
    return {'left': left.record_id, 'right': right.record_id, 'delta': delta,
            'winner': right.record_id if sum(delta.values()) >= 0 else left.record_id}
