from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from consensus_workbench.agenda.item_contract import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_working_group_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_working_group_presence_threshold', 10.333)
    return _result('check_working_group_presence', adjusted, threshold, True, 'validates working_group presence',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_working_group_range_threshold', 12.667)
    return _result('check_working_group_range', adjusted, threshold, True, 'validates working_group range',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_working_group_stability_threshold', 15.0)
    return _result('check_working_group_stability', adjusted, threshold, False, 'validates working_group stability',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_working_group_freshness_threshold', 17.333)
    return _result('check_working_group_freshness', adjusted, threshold, True, 'validates working_group freshness',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_working_group_coverage_threshold', 19.667)
    return _result('check_working_group_coverage', adjusted, threshold, True, 'validates working_group coverage',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_working_group_consistency_threshold', 22.0)
    return _result('check_working_group_consistency', adjusted, threshold, False, 'validates working_group consistency',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_working_group_risk_threshold', 24.333)
    return _result('check_working_group_risk', adjusted, threshold, True, 'validates working_group risk',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_working_group_confidence_threshold', 26.667)
    return _result('check_working_group_confidence', adjusted, threshold, True, 'validates working_group confidence',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_working_group_dependency_threshold', 29.0)
    return _result('check_working_group_dependency', adjusted, threshold, False, 'validates working_group dependency',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_working_group_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'working_group')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_working_group_readiness_threshold', 31.333)
    return _result('check_working_group_readiness', adjusted, threshold, True, 'validates working_group readiness',
                   {'field': 'working_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_issue_urgency_presence_threshold', 9.333)
    return _result('check_issue_urgency_presence', adjusted, threshold, True, 'validates issue_urgency presence',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_issue_urgency_range_threshold', 11.667)
    return _result('check_issue_urgency_range', adjusted, threshold, False, 'validates issue_urgency range',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_issue_urgency_stability_threshold', 14.0)
    return _result('check_issue_urgency_stability', adjusted, threshold, True, 'validates issue_urgency stability',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_issue_urgency_freshness_threshold', 16.333)
    return _result('check_issue_urgency_freshness', adjusted, threshold, True, 'validates issue_urgency freshness',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_issue_urgency_coverage_threshold', 18.667)
    return _result('check_issue_urgency_coverage', adjusted, threshold, False, 'validates issue_urgency coverage',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_issue_urgency_consistency_threshold', 21.0)
    return _result('check_issue_urgency_consistency', adjusted, threshold, True, 'validates issue_urgency consistency',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_issue_urgency_risk_threshold', 23.333)
    return _result('check_issue_urgency_risk', adjusted, threshold, True, 'validates issue_urgency risk',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_issue_urgency_confidence_threshold', 25.667)
    return _result('check_issue_urgency_confidence', adjusted, threshold, False, 'validates issue_urgency confidence',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_issue_urgency_dependency_threshold', 28.0)
    return _result('check_issue_urgency_dependency', adjusted, threshold, True, 'validates issue_urgency dependency',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_issue_urgency_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'issue_urgency')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_issue_urgency_readiness_threshold', 30.333)
    return _result('check_issue_urgency_readiness', adjusted, threshold, True, 'validates issue_urgency readiness',
                   {'field': 'issue_urgency', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_evidence_maturity_presence_threshold', 8.333)
    return _result('check_evidence_maturity_presence', adjusted, threshold, False, 'validates evidence_maturity presence',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_evidence_maturity_range_threshold', 10.667)
    return _result('check_evidence_maturity_range', adjusted, threshold, True, 'validates evidence_maturity range',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_evidence_maturity_stability_threshold', 13.0)
    return _result('check_evidence_maturity_stability', adjusted, threshold, True, 'validates evidence_maturity stability',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_evidence_maturity_freshness_threshold', 15.333)
    return _result('check_evidence_maturity_freshness', adjusted, threshold, False, 'validates evidence_maturity freshness',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_evidence_maturity_coverage_threshold', 17.667)
    return _result('check_evidence_maturity_coverage', adjusted, threshold, True, 'validates evidence_maturity coverage',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_evidence_maturity_consistency_threshold', 20.0)
    return _result('check_evidence_maturity_consistency', adjusted, threshold, True, 'validates evidence_maturity consistency',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_evidence_maturity_risk_threshold', 22.333)
    return _result('check_evidence_maturity_risk', adjusted, threshold, False, 'validates evidence_maturity risk',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_evidence_maturity_confidence_threshold', 24.667)
    return _result('check_evidence_maturity_confidence', adjusted, threshold, True, 'validates evidence_maturity confidence',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_evidence_maturity_dependency_threshold', 27.0)
    return _result('check_evidence_maturity_dependency', adjusted, threshold, True, 'validates evidence_maturity dependency',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_maturity_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_maturity')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_evidence_maturity_readiness_threshold', 29.333)
    return _result('check_evidence_maturity_readiness', adjusted, threshold, False, 'validates evidence_maturity readiness',
                   {'field': 'evidence_maturity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_deliberation_window_presence_threshold', 31.667)
    return _result('check_deliberation_window_presence', adjusted, threshold, True, 'validates deliberation_window presence',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_deliberation_window_range_threshold', 9.667)
    return _result('check_deliberation_window_range', adjusted, threshold, True, 'validates deliberation_window range',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_deliberation_window_stability_threshold', 12.0)
    return _result('check_deliberation_window_stability', adjusted, threshold, False, 'validates deliberation_window stability',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_deliberation_window_freshness_threshold', 14.333)
    return _result('check_deliberation_window_freshness', adjusted, threshold, True, 'validates deliberation_window freshness',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_deliberation_window_coverage_threshold', 16.667)
    return _result('check_deliberation_window_coverage', adjusted, threshold, True, 'validates deliberation_window coverage',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_deliberation_window_consistency_threshold', 19.0)
    return _result('check_deliberation_window_consistency', adjusted, threshold, False, 'validates deliberation_window consistency',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_deliberation_window_risk_threshold', 21.333)
    return _result('check_deliberation_window_risk', adjusted, threshold, True, 'validates deliberation_window risk',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_deliberation_window_confidence_threshold', 23.667)
    return _result('check_deliberation_window_confidence', adjusted, threshold, True, 'validates deliberation_window confidence',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_deliberation_window_dependency_threshold', 26.0)
    return _result('check_deliberation_window_dependency', adjusted, threshold, False, 'validates deliberation_window dependency',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deliberation_window_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deliberation_window')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_deliberation_window_readiness_threshold', 28.333)
    return _result('check_deliberation_window_readiness', adjusted, threshold, True, 'validates deliberation_window readiness',
                   {'field': 'deliberation_window', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_resource_band_presence_threshold', 30.667)
    return _result('check_resource_band_presence', adjusted, threshold, True, 'validates resource_band presence',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_resource_band_range_threshold', 8.667)
    return _result('check_resource_band_range', adjusted, threshold, False, 'validates resource_band range',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_resource_band_stability_threshold', 11.0)
    return _result('check_resource_band_stability', adjusted, threshold, True, 'validates resource_band stability',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_resource_band_freshness_threshold', 13.333)
    return _result('check_resource_band_freshness', adjusted, threshold, True, 'validates resource_band freshness',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_resource_band_coverage_threshold', 15.667)
    return _result('check_resource_band_coverage', adjusted, threshold, False, 'validates resource_band coverage',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_resource_band_consistency_threshold', 18.0)
    return _result('check_resource_band_consistency', adjusted, threshold, True, 'validates resource_band consistency',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_resource_band_risk_threshold', 20.333)
    return _result('check_resource_band_risk', adjusted, threshold, True, 'validates resource_band risk',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_resource_band_confidence_threshold', 22.667)
    return _result('check_resource_band_confidence', adjusted, threshold, False, 'validates resource_band confidence',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_resource_band_dependency_threshold', 25.0)
    return _result('check_resource_band_dependency', adjusted, threshold, True, 'validates resource_band dependency',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_band_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_band')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_resource_band_readiness_threshold', 27.333)
    return _result('check_resource_band_readiness', adjusted, threshold, True, 'validates resource_band readiness',
                   {'field': 'resource_band', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_risk_class_presence_threshold', 29.667)
    return _result('check_risk_class_presence', adjusted, threshold, False, 'validates risk_class presence',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_risk_class_range_threshold', 32.0)
    return _result('check_risk_class_range', adjusted, threshold, True, 'validates risk_class range',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_risk_class_stability_threshold', 10.0)
    return _result('check_risk_class_stability', adjusted, threshold, True, 'validates risk_class stability',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_risk_class_freshness_threshold', 12.333)
    return _result('check_risk_class_freshness', adjusted, threshold, False, 'validates risk_class freshness',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_risk_class_coverage_threshold', 14.667)
    return _result('check_risk_class_coverage', adjusted, threshold, True, 'validates risk_class coverage',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_risk_class_consistency_threshold', 17.0)
    return _result('check_risk_class_consistency', adjusted, threshold, True, 'validates risk_class consistency',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_risk_class_risk_threshold', 19.333)
    return _result('check_risk_class_risk', adjusted, threshold, False, 'validates risk_class risk',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_risk_class_confidence_threshold', 21.667)
    return _result('check_risk_class_confidence', adjusted, threshold, True, 'validates risk_class confidence',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_risk_class_dependency_threshold', 24.0)
    return _result('check_risk_class_dependency', adjusted, threshold, True, 'validates risk_class dependency',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_class_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_class')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_risk_class_readiness_threshold', 26.333)
    return _result('check_risk_class_readiness', adjusted, threshold, False, 'validates risk_class readiness',
                   {'field': 'risk_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_regional_relevance_presence_threshold', 28.667)
    return _result('check_regional_relevance_presence', adjusted, threshold, True, 'validates regional_relevance presence',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_regional_relevance_range_threshold', 31.0)
    return _result('check_regional_relevance_range', adjusted, threshold, True, 'validates regional_relevance range',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_regional_relevance_stability_threshold', 9.0)
    return _result('check_regional_relevance_stability', adjusted, threshold, False, 'validates regional_relevance stability',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_regional_relevance_freshness_threshold', 11.333)
    return _result('check_regional_relevance_freshness', adjusted, threshold, True, 'validates regional_relevance freshness',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_regional_relevance_coverage_threshold', 13.667)
    return _result('check_regional_relevance_coverage', adjusted, threshold, True, 'validates regional_relevance coverage',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_regional_relevance_consistency_threshold', 16.0)
    return _result('check_regional_relevance_consistency', adjusted, threshold, False, 'validates regional_relevance consistency',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_regional_relevance_risk_threshold', 18.333)
    return _result('check_regional_relevance_risk', adjusted, threshold, True, 'validates regional_relevance risk',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_regional_relevance_confidence_threshold', 20.667)
    return _result('check_regional_relevance_confidence', adjusted, threshold, True, 'validates regional_relevance confidence',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_regional_relevance_dependency_threshold', 23.0)
    return _result('check_regional_relevance_dependency', adjusted, threshold, False, 'validates regional_relevance dependency',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_regional_relevance_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'regional_relevance')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_regional_relevance_readiness_threshold', 25.333)
    return _result('check_regional_relevance_readiness', adjusted, threshold, True, 'validates regional_relevance readiness',
                   {'field': 'regional_relevance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_dependency_count_presence_threshold', 27.667)
    return _result('check_dependency_count_presence', adjusted, threshold, True, 'validates dependency_count presence',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_dependency_count_range_threshold', 30.0)
    return _result('check_dependency_count_range', adjusted, threshold, False, 'validates dependency_count range',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_dependency_count_stability_threshold', 8.0)
    return _result('check_dependency_count_stability', adjusted, threshold, True, 'validates dependency_count stability',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_dependency_count_freshness_threshold', 10.333)
    return _result('check_dependency_count_freshness', adjusted, threshold, True, 'validates dependency_count freshness',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_dependency_count_coverage_threshold', 12.667)
    return _result('check_dependency_count_coverage', adjusted, threshold, False, 'validates dependency_count coverage',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_dependency_count_consistency_threshold', 15.0)
    return _result('check_dependency_count_consistency', adjusted, threshold, True, 'validates dependency_count consistency',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_dependency_count_risk_threshold', 17.333)
    return _result('check_dependency_count_risk', adjusted, threshold, True, 'validates dependency_count risk',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_dependency_count_confidence_threshold', 19.667)
    return _result('check_dependency_count_confidence', adjusted, threshold, False, 'validates dependency_count confidence',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_dependency_count_dependency_threshold', 22.0)
    return _result('check_dependency_count_dependency', adjusted, threshold, True, 'validates dependency_count dependency',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_dependency_count_readiness_threshold', 24.333)
    return _result('check_dependency_count_readiness', adjusted, threshold, True, 'validates dependency_count readiness',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_expert_capacity_presence_threshold', 26.667)
    return _result('check_expert_capacity_presence', adjusted, threshold, False, 'validates expert_capacity presence',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_expert_capacity_range_threshold', 29.0)
    return _result('check_expert_capacity_range', adjusted, threshold, True, 'validates expert_capacity range',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_expert_capacity_stability_threshold', 31.333)
    return _result('check_expert_capacity_stability', adjusted, threshold, True, 'validates expert_capacity stability',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_expert_capacity_freshness_threshold', 9.333)
    return _result('check_expert_capacity_freshness', adjusted, threshold, False, 'validates expert_capacity freshness',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_expert_capacity_coverage_threshold', 11.667)
    return _result('check_expert_capacity_coverage', adjusted, threshold, True, 'validates expert_capacity coverage',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_expert_capacity_consistency_threshold', 14.0)
    return _result('check_expert_capacity_consistency', adjusted, threshold, True, 'validates expert_capacity consistency',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_expert_capacity_risk_threshold', 16.333)
    return _result('check_expert_capacity_risk', adjusted, threshold, False, 'validates expert_capacity risk',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_expert_capacity_confidence_threshold', 18.667)
    return _result('check_expert_capacity_confidence', adjusted, threshold, True, 'validates expert_capacity confidence',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_expert_capacity_dependency_threshold', 21.0)
    return _result('check_expert_capacity_dependency', adjusted, threshold, True, 'validates expert_capacity dependency',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expert_capacity_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expert_capacity')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_expert_capacity_readiness_threshold', 23.333)
    return _result('check_expert_capacity_readiness', adjusted, threshold, False, 'validates expert_capacity readiness',
                   {'field': 'expert_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_evidence_strength_presence_threshold', 25.667)
    return _result('check_evidence_strength_presence', adjusted, threshold, True, 'validates evidence_strength presence',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_evidence_strength_range_threshold', 28.0)
    return _result('check_evidence_strength_range', adjusted, threshold, True, 'validates evidence_strength range',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_evidence_strength_stability_threshold', 30.333)
    return _result('check_evidence_strength_stability', adjusted, threshold, False, 'validates evidence_strength stability',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_evidence_strength_freshness_threshold', 8.333)
    return _result('check_evidence_strength_freshness', adjusted, threshold, True, 'validates evidence_strength freshness',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_evidence_strength_coverage_threshold', 10.667)
    return _result('check_evidence_strength_coverage', adjusted, threshold, True, 'validates evidence_strength coverage',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_evidence_strength_consistency_threshold', 13.0)
    return _result('check_evidence_strength_consistency', adjusted, threshold, False, 'validates evidence_strength consistency',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_evidence_strength_risk_threshold', 15.333)
    return _result('check_evidence_strength_risk', adjusted, threshold, True, 'validates evidence_strength risk',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_evidence_strength_confidence_threshold', 17.667)
    return _result('check_evidence_strength_confidence', adjusted, threshold, True, 'validates evidence_strength confidence',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_evidence_strength_dependency_threshold', 20.0)
    return _result('check_evidence_strength_dependency', adjusted, threshold, False, 'validates evidence_strength dependency',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_strength_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_strength')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_evidence_strength_readiness_threshold', 22.333)
    return _result('check_evidence_strength_readiness', adjusted, threshold, True, 'validates evidence_strength readiness',
                   {'field': 'evidence_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_conflict_count_presence_threshold', 24.667)
    return _result('check_conflict_count_presence', adjusted, threshold, True, 'validates conflict_count presence',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_conflict_count_range_threshold', 27.0)
    return _result('check_conflict_count_range', adjusted, threshold, False, 'validates conflict_count range',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_conflict_count_stability_threshold', 29.333)
    return _result('check_conflict_count_stability', adjusted, threshold, True, 'validates conflict_count stability',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_conflict_count_freshness_threshold', 31.667)
    return _result('check_conflict_count_freshness', adjusted, threshold, True, 'validates conflict_count freshness',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_conflict_count_coverage_threshold', 9.667)
    return _result('check_conflict_count_coverage', adjusted, threshold, False, 'validates conflict_count coverage',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_conflict_count_consistency_threshold', 12.0)
    return _result('check_conflict_count_consistency', adjusted, threshold, True, 'validates conflict_count consistency',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_conflict_count_risk_threshold', 14.333)
    return _result('check_conflict_count_risk', adjusted, threshold, True, 'validates conflict_count risk',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_conflict_count_confidence_threshold', 16.667)
    return _result('check_conflict_count_confidence', adjusted, threshold, False, 'validates conflict_count confidence',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_conflict_count_dependency_threshold', 19.0)
    return _result('check_conflict_count_dependency', adjusted, threshold, True, 'validates conflict_count dependency',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_conflict_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'conflict_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_conflict_count_readiness_threshold', 21.333)
    return _result('check_conflict_count_readiness', adjusted, threshold, True, 'validates conflict_count readiness',
                   {'field': 'conflict_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_public_value_presence_threshold', 23.667)
    return _result('check_public_value_presence', adjusted, threshold, False, 'validates public_value presence',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_public_value_range_threshold', 26.0)
    return _result('check_public_value_range', adjusted, threshold, True, 'validates public_value range',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_public_value_stability_threshold', 28.333)
    return _result('check_public_value_stability', adjusted, threshold, True, 'validates public_value stability',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_public_value_freshness_threshold', 30.667)
    return _result('check_public_value_freshness', adjusted, threshold, False, 'validates public_value freshness',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_public_value_coverage_threshold', 8.667)
    return _result('check_public_value_coverage', adjusted, threshold, True, 'validates public_value coverage',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_public_value_consistency_threshold', 11.0)
    return _result('check_public_value_consistency', adjusted, threshold, True, 'validates public_value consistency',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_public_value_risk_threshold', 13.333)
    return _result('check_public_value_risk', adjusted, threshold, False, 'validates public_value risk',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_public_value_confidence_threshold', 15.667)
    return _result('check_public_value_confidence', adjusted, threshold, True, 'validates public_value confidence',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_public_value_dependency_threshold', 18.0)
    return _result('check_public_value_dependency', adjusted, threshold, True, 'validates public_value dependency',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_public_value_readiness_threshold', 20.333)
    return _result('check_public_value_readiness', adjusted, threshold, False, 'validates public_value readiness',
                   {'field': 'public_value', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_working_group_presence,
    check_working_group_range,
    check_working_group_stability,
    check_working_group_freshness,
    check_working_group_coverage,
    check_working_group_consistency,
    check_working_group_risk,
    check_working_group_confidence,
    check_working_group_dependency,
    check_working_group_readiness,
    check_issue_urgency_presence,
    check_issue_urgency_range,
    check_issue_urgency_stability,
    check_issue_urgency_freshness,
    check_issue_urgency_coverage,
    check_issue_urgency_consistency,
    check_issue_urgency_risk,
    check_issue_urgency_confidence,
    check_issue_urgency_dependency,
    check_issue_urgency_readiness,
    check_evidence_maturity_presence,
    check_evidence_maturity_range,
    check_evidence_maturity_stability,
    check_evidence_maturity_freshness,
    check_evidence_maturity_coverage,
    check_evidence_maturity_consistency,
    check_evidence_maturity_risk,
    check_evidence_maturity_confidence,
    check_evidence_maturity_dependency,
    check_evidence_maturity_readiness,
    check_deliberation_window_presence,
    check_deliberation_window_range,
    check_deliberation_window_stability,
    check_deliberation_window_freshness,
    check_deliberation_window_coverage,
    check_deliberation_window_consistency,
    check_deliberation_window_risk,
    check_deliberation_window_confidence,
    check_deliberation_window_dependency,
    check_deliberation_window_readiness,
    check_resource_band_presence,
    check_resource_band_range,
    check_resource_band_stability,
    check_resource_band_freshness,
    check_resource_band_coverage,
    check_resource_band_consistency,
    check_resource_band_risk,
    check_resource_band_confidence,
    check_resource_band_dependency,
    check_resource_band_readiness,
    check_risk_class_presence,
    check_risk_class_range,
    check_risk_class_stability,
    check_risk_class_freshness,
    check_risk_class_coverage,
    check_risk_class_consistency,
    check_risk_class_risk,
    check_risk_class_confidence,
    check_risk_class_dependency,
    check_risk_class_readiness,
    check_regional_relevance_presence,
    check_regional_relevance_range,
    check_regional_relevance_stability,
    check_regional_relevance_freshness,
    check_regional_relevance_coverage,
    check_regional_relevance_consistency,
    check_regional_relevance_risk,
    check_regional_relevance_confidence,
    check_regional_relevance_dependency,
    check_regional_relevance_readiness,
    check_dependency_count_presence,
    check_dependency_count_range,
    check_dependency_count_stability,
    check_dependency_count_freshness,
    check_dependency_count_coverage,
    check_dependency_count_consistency,
    check_dependency_count_risk,
    check_dependency_count_confidence,
    check_dependency_count_dependency,
    check_dependency_count_readiness,
    check_expert_capacity_presence,
    check_expert_capacity_range,
    check_expert_capacity_stability,
    check_expert_capacity_freshness,
    check_expert_capacity_coverage,
    check_expert_capacity_consistency,
    check_expert_capacity_risk,
    check_expert_capacity_confidence,
    check_expert_capacity_dependency,
    check_expert_capacity_readiness,
    check_evidence_strength_presence,
    check_evidence_strength_range,
    check_evidence_strength_stability,
    check_evidence_strength_freshness,
    check_evidence_strength_coverage,
    check_evidence_strength_consistency,
    check_evidence_strength_risk,
    check_evidence_strength_confidence,
    check_evidence_strength_dependency,
    check_evidence_strength_readiness,
    check_conflict_count_presence,
    check_conflict_count_range,
    check_conflict_count_stability,
    check_conflict_count_freshness,
    check_conflict_count_coverage,
    check_conflict_count_consistency,
    check_conflict_count_risk,
    check_conflict_count_confidence,
    check_conflict_count_dependency,
    check_conflict_count_readiness,
    check_public_value_presence,
    check_public_value_range,
    check_public_value_stability,
    check_public_value_freshness,
    check_public_value_coverage,
    check_public_value_consistency,
    check_public_value_risk,
    check_public_value_confidence,
    check_public_value_dependency,
    check_public_value_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
