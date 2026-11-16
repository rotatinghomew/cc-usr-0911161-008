from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from consensus_workbench.agenda.item_contract import ContractError, Decision, DomainRecord, RuleResult, bounded
from consensus_workbench.agenda_board.portfolio_selection import grouped_metrics, record_score
from consensus_workbench.evidence.conflict_rules import evaluate

STATES = ['submitted', 'scoped', 'deliberating', 'balloting', 'adopted', 'reopened']
TRANSITIONS = {state: tuple(STATES[i + 1:i + 3]) for i, state in enumerate(STATES)}

@dataclass(frozen=True)
class TransitionPlan:
    from_state: str
    to_state: str
    allowed: bool
    reasons: tuple[str, ...]
    score: float

def allowed_targets(state: str) -> tuple[str, ...]:
    if state not in TRANSITIONS:
        raise ContractError('unknown workflow state')
    return TRANSITIONS[state]

def plan_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> TransitionPlan:
    context = context or {}
    if target not in STATES:
        raise ContractError('unknown target state')
    scorecard = record_score(record, context)
    reasons: list[str] = []
    structurally_allowed = target in allowed_targets(record.state)
    if not structurally_allowed:
        reasons.append('transition is not adjacent in the lifecycle')
    threshold = float(context.get('transition_threshold', 0.42))
    if scorecard['score'] < threshold:
        reasons.append('record score is below the transition threshold')
    return TransitionPlan(record.state, target, structurally_allowed and not reasons, tuple(reasons or ['eligible']), scorecard['score'])

def apply_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> DomainRecord:
    plan = plan_transition(record, target, context)
    if not plan.allowed:
        raise ContractError('; '.join(plan.reasons))
    return record.with_state(target)

def guard_working_group_match_fit_01(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_working_group_match_fit_01_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_match_fit_01' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_disclosure_quality_02(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_issue_urgency_disclosure_quality_02_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_disclosure_quality_02' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_pilot_feasibility_03(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_evidence_maturity_pilot_feasibility_03_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_pilot_feasibility_03' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_supplier_concentration_04(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_deliberation_window_supplier_concentration_04_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_supplier_concentration_04' + (':passed' if allowed else ':blocked')

def guard_resource_band_evidence_velocity_05(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_resource_band_evidence_velocity_05_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_evidence_velocity_05' + (':passed' if allowed else ':blocked')

def guard_risk_class_benefit_confidence_06(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_risk_class_benefit_confidence_06_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_benefit_confidence_06' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_exit_risk_07(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_regional_relevance_exit_risk_07_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_exit_risk_07' + (':passed' if allowed else ':blocked')

def guard_dependency_count_agenda_board_balance_08(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_dependency_count_agenda_board_balance_08_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_agenda_board_balance_08' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_match_fit_09(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_expert_capacity_match_fit_09_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_match_fit_09' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_disclosure_quality_10(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_evidence_strength_disclosure_quality_10_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_disclosure_quality_10' + (':passed' if allowed else ':blocked')

def guard_conflict_count_pilot_feasibility_11(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_conflict_count_pilot_feasibility_11_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_pilot_feasibility_11' + (':passed' if allowed else ':blocked')

def guard_public_value_supplier_concentration_12(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_public_value_supplier_concentration_12_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_supplier_concentration_12' + (':passed' if allowed else ':blocked')

def guard_working_group_evidence_velocity_13(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_working_group_evidence_velocity_13_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_evidence_velocity_13' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_benefit_confidence_14(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_issue_urgency_benefit_confidence_14_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_benefit_confidence_14' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_exit_risk_15(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_evidence_maturity_exit_risk_15_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_exit_risk_15' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_agenda_board_balance_16(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_deliberation_window_agenda_board_balance_16_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_agenda_board_balance_16' + (':passed' if allowed else ':blocked')

def guard_resource_band_match_fit_17(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_resource_band_match_fit_17_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_match_fit_17' + (':passed' if allowed else ':blocked')

def guard_risk_class_disclosure_quality_18(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_risk_class_disclosure_quality_18_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_disclosure_quality_18' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_pilot_feasibility_19(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_regional_relevance_pilot_feasibility_19_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_pilot_feasibility_19' + (':passed' if allowed else ':blocked')

def guard_dependency_count_supplier_concentration_20(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_dependency_count_supplier_concentration_20_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_supplier_concentration_20' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_evidence_velocity_21(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_expert_capacity_evidence_velocity_21_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_evidence_velocity_21' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_benefit_confidence_22(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_evidence_strength_benefit_confidence_22_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_benefit_confidence_22' + (':passed' if allowed else ':blocked')

def guard_conflict_count_exit_risk_23(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_conflict_count_exit_risk_23_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_exit_risk_23' + (':passed' if allowed else ':blocked')

def guard_public_value_agenda_board_balance_24(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_public_value_agenda_board_balance_24_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_agenda_board_balance_24' + (':passed' if allowed else ':blocked')

def guard_working_group_match_fit_25(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_working_group_match_fit_25_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_match_fit_25' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_disclosure_quality_26(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_issue_urgency_disclosure_quality_26_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_disclosure_quality_26' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_pilot_feasibility_27(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_evidence_maturity_pilot_feasibility_27_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_pilot_feasibility_27' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_supplier_concentration_28(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_deliberation_window_supplier_concentration_28_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_supplier_concentration_28' + (':passed' if allowed else ':blocked')

def guard_resource_band_evidence_velocity_29(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_resource_band_evidence_velocity_29_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_evidence_velocity_29' + (':passed' if allowed else ':blocked')

def guard_risk_class_benefit_confidence_30(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_risk_class_benefit_confidence_30_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_benefit_confidence_30' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_exit_risk_31(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_regional_relevance_exit_risk_31_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_exit_risk_31' + (':passed' if allowed else ':blocked')

def guard_dependency_count_agenda_board_balance_32(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_dependency_count_agenda_board_balance_32_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_agenda_board_balance_32' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_match_fit_33(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_expert_capacity_match_fit_33_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_match_fit_33' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_disclosure_quality_34(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_evidence_strength_disclosure_quality_34_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_disclosure_quality_34' + (':passed' if allowed else ':blocked')

def guard_conflict_count_pilot_feasibility_35(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_conflict_count_pilot_feasibility_35_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_pilot_feasibility_35' + (':passed' if allowed else ':blocked')

def guard_public_value_supplier_concentration_36(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_public_value_supplier_concentration_36_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_supplier_concentration_36' + (':passed' if allowed else ':blocked')

def guard_working_group_evidence_velocity_37(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_working_group_evidence_velocity_37_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_evidence_velocity_37' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_benefit_confidence_38(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_issue_urgency_benefit_confidence_38_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_benefit_confidence_38' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_exit_risk_39(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_evidence_maturity_exit_risk_39_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_exit_risk_39' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_agenda_board_balance_40(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_deliberation_window_agenda_board_balance_40_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_agenda_board_balance_40' + (':passed' if allowed else ':blocked')

def guard_resource_band_match_fit_41(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_resource_band_match_fit_41_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_match_fit_41' + (':passed' if allowed else ':blocked')

def guard_risk_class_disclosure_quality_42(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_risk_class_disclosure_quality_42_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_disclosure_quality_42' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_pilot_feasibility_43(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_regional_relevance_pilot_feasibility_43_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_pilot_feasibility_43' + (':passed' if allowed else ':blocked')

def guard_dependency_count_supplier_concentration_44(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_dependency_count_supplier_concentration_44_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_supplier_concentration_44' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_evidence_velocity_45(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_expert_capacity_evidence_velocity_45_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_evidence_velocity_45' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_benefit_confidence_46(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_evidence_strength_benefit_confidence_46_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_benefit_confidence_46' + (':passed' if allowed else ':blocked')

def guard_conflict_count_exit_risk_47(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_conflict_count_exit_risk_47_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_exit_risk_47' + (':passed' if allowed else ':blocked')

def guard_public_value_agenda_board_balance_48(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_public_value_agenda_board_balance_48_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_agenda_board_balance_48' + (':passed' if allowed else ':blocked')

def guard_working_group_match_fit_49(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_working_group_match_fit_49_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_match_fit_49' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_disclosure_quality_50(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_issue_urgency_disclosure_quality_50_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_disclosure_quality_50' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_pilot_feasibility_51(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_evidence_maturity_pilot_feasibility_51_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_pilot_feasibility_51' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_supplier_concentration_52(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_deliberation_window_supplier_concentration_52_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_supplier_concentration_52' + (':passed' if allowed else ':blocked')

def guard_resource_band_evidence_velocity_53(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_resource_band_evidence_velocity_53_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_evidence_velocity_53' + (':passed' if allowed else ':blocked')

def guard_risk_class_benefit_confidence_54(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_risk_class_benefit_confidence_54_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_benefit_confidence_54' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_exit_risk_55(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_regional_relevance_exit_risk_55_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_exit_risk_55' + (':passed' if allowed else ':blocked')

def guard_dependency_count_agenda_board_balance_56(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_dependency_count_agenda_board_balance_56_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_agenda_board_balance_56' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_match_fit_57(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_expert_capacity_match_fit_57_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_match_fit_57' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_disclosure_quality_58(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_evidence_strength_disclosure_quality_58_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_disclosure_quality_58' + (':passed' if allowed else ':blocked')

def guard_conflict_count_pilot_feasibility_59(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_conflict_count_pilot_feasibility_59_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_pilot_feasibility_59' + (':passed' if allowed else ':blocked')

def guard_public_value_supplier_concentration_60(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_public_value_supplier_concentration_60_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_supplier_concentration_60' + (':passed' if allowed else ':blocked')

def guard_working_group_evidence_velocity_61(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_working_group_evidence_velocity_61_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_evidence_velocity_61' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_benefit_confidence_62(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_issue_urgency_benefit_confidence_62_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_benefit_confidence_62' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_exit_risk_63(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_evidence_maturity_exit_risk_63_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_exit_risk_63' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_agenda_board_balance_64(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_deliberation_window_agenda_board_balance_64_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_agenda_board_balance_64' + (':passed' if allowed else ':blocked')

def guard_resource_band_match_fit_65(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_resource_band_match_fit_65_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_match_fit_65' + (':passed' if allowed else ':blocked')

def guard_risk_class_disclosure_quality_66(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_risk_class_disclosure_quality_66_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_disclosure_quality_66' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_pilot_feasibility_67(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_regional_relevance_pilot_feasibility_67_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_pilot_feasibility_67' + (':passed' if allowed else ':blocked')

def guard_dependency_count_supplier_concentration_68(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_dependency_count_supplier_concentration_68_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_supplier_concentration_68' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_evidence_velocity_69(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_expert_capacity_evidence_velocity_69_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_evidence_velocity_69' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_benefit_confidence_70(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_evidence_strength_benefit_confidence_70_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_benefit_confidence_70' + (':passed' if allowed else ':blocked')

def guard_conflict_count_exit_risk_71(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_conflict_count_exit_risk_71_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_exit_risk_71' + (':passed' if allowed else ':blocked')

def guard_public_value_agenda_board_balance_72(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_public_value_agenda_board_balance_72_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_agenda_board_balance_72' + (':passed' if allowed else ':blocked')

def guard_working_group_match_fit_73(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_working_group_match_fit_73_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_match_fit_73' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_disclosure_quality_74(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_issue_urgency_disclosure_quality_74_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_disclosure_quality_74' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_pilot_feasibility_75(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_evidence_maturity_pilot_feasibility_75_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_pilot_feasibility_75' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_supplier_concentration_76(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_deliberation_window_supplier_concentration_76_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_supplier_concentration_76' + (':passed' if allowed else ':blocked')

def guard_resource_band_evidence_velocity_77(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_resource_band_evidence_velocity_77_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_evidence_velocity_77' + (':passed' if allowed else ':blocked')

def guard_risk_class_benefit_confidence_78(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_risk_class_benefit_confidence_78_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_benefit_confidence_78' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_exit_risk_79(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_regional_relevance_exit_risk_79_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_exit_risk_79' + (':passed' if allowed else ':blocked')

def guard_dependency_count_agenda_board_balance_80(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_dependency_count_agenda_board_balance_80_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_agenda_board_balance_80' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_match_fit_81(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_expert_capacity_match_fit_81_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_match_fit_81' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_disclosure_quality_82(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_evidence_strength_disclosure_quality_82_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_disclosure_quality_82' + (':passed' if allowed else ':blocked')

def guard_conflict_count_pilot_feasibility_83(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_conflict_count_pilot_feasibility_83_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_pilot_feasibility_83' + (':passed' if allowed else ':blocked')

def guard_public_value_supplier_concentration_84(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_public_value_supplier_concentration_84_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_supplier_concentration_84' + (':passed' if allowed else ':blocked')

def guard_working_group_evidence_velocity_85(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_working_group_evidence_velocity_85_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_evidence_velocity_85' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_benefit_confidence_86(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_issue_urgency_benefit_confidence_86_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_benefit_confidence_86' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_exit_risk_87(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_evidence_maturity_exit_risk_87_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_exit_risk_87' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_agenda_board_balance_88(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_deliberation_window_agenda_board_balance_88_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_agenda_board_balance_88' + (':passed' if allowed else ':blocked')

def guard_resource_band_match_fit_89(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_resource_band_match_fit_89_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_match_fit_89' + (':passed' if allowed else ':blocked')

def guard_risk_class_disclosure_quality_90(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_risk_class_disclosure_quality_90_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_disclosure_quality_90' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_pilot_feasibility_91(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_regional_relevance_pilot_feasibility_91_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_pilot_feasibility_91' + (':passed' if allowed else ':blocked')

def guard_dependency_count_supplier_concentration_92(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_dependency_count_supplier_concentration_92_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_supplier_concentration_92' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_evidence_velocity_93(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_expert_capacity_evidence_velocity_93_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_evidence_velocity_93' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_benefit_confidence_94(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_evidence_strength_benefit_confidence_94_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_benefit_confidence_94' + (':passed' if allowed else ':blocked')

def guard_conflict_count_exit_risk_95(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_conflict_count_exit_risk_95_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_exit_risk_95' + (':passed' if allowed else ':blocked')

def guard_public_value_agenda_board_balance_96(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_public_value_agenda_board_balance_96_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_agenda_board_balance_96' + (':passed' if allowed else ':blocked')

def guard_working_group_match_fit_97(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_working_group_match_fit_97_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_match_fit_97' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_disclosure_quality_98(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_issue_urgency_disclosure_quality_98_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_disclosure_quality_98' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_pilot_feasibility_99(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_evidence_maturity_pilot_feasibility_99_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_pilot_feasibility_99' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_supplier_concentration_100(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_deliberation_window_supplier_concentration_100_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_supplier_concentration_100' + (':passed' if allowed else ':blocked')

def guard_resource_band_evidence_velocity_101(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_resource_band_evidence_velocity_101_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_evidence_velocity_101' + (':passed' if allowed else ':blocked')

def guard_risk_class_benefit_confidence_102(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_risk_class_benefit_confidence_102_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_benefit_confidence_102' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_exit_risk_103(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_regional_relevance_exit_risk_103_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_exit_risk_103' + (':passed' if allowed else ':blocked')

def guard_dependency_count_agenda_board_balance_104(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_dependency_count_agenda_board_balance_104_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_agenda_board_balance_104' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_match_fit_105(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_expert_capacity_match_fit_105_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_match_fit_105' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_disclosure_quality_106(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_evidence_strength_disclosure_quality_106_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_disclosure_quality_106' + (':passed' if allowed else ':blocked')

def guard_conflict_count_pilot_feasibility_107(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_conflict_count_pilot_feasibility_107_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_pilot_feasibility_107' + (':passed' if allowed else ':blocked')

def guard_public_value_supplier_concentration_108(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_public_value_supplier_concentration_108_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_supplier_concentration_108' + (':passed' if allowed else ':blocked')

def guard_working_group_evidence_velocity_109(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_working_group_evidence_velocity_109_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_working_group_evidence_velocity_109' + (':passed' if allowed else ':blocked')

def guard_issue_urgency_benefit_confidence_110(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_issue_urgency_benefit_confidence_110_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_issue_urgency_benefit_confidence_110' + (':passed' if allowed else ':blocked')

def guard_evidence_maturity_exit_risk_111(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_evidence_maturity_exit_risk_111_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_maturity_exit_risk_111' + (':passed' if allowed else ':blocked')

def guard_deliberation_window_agenda_board_balance_112(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_deliberation_window_agenda_board_balance_112_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_deliberation_window_agenda_board_balance_112' + (':passed' if allowed else ':blocked')

def guard_resource_band_match_fit_113(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('match_fit', 0.0)
    floor = float(context.get('guard_resource_band_match_fit_113_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_band_match_fit_113' + (':passed' if allowed else ':blocked')

def guard_risk_class_disclosure_quality_114(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('disclosure_quality', 0.0)
    floor = float(context.get('guard_risk_class_disclosure_quality_114_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_class_disclosure_quality_114' + (':passed' if allowed else ':blocked')

def guard_regional_relevance_pilot_feasibility_115(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('pilot_feasibility', 0.0)
    floor = float(context.get('guard_regional_relevance_pilot_feasibility_115_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_regional_relevance_pilot_feasibility_115' + (':passed' if allowed else ':blocked')

def guard_dependency_count_supplier_concentration_116(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('supplier_concentration', 0.0)
    floor = float(context.get('guard_dependency_count_supplier_concentration_116_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('scoped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_supplier_concentration_116' + (':passed' if allowed else ':blocked')

def guard_expert_capacity_evidence_velocity_117(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_velocity', 0.0)
    floor = float(context.get('guard_expert_capacity_evidence_velocity_117_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('deliberating')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_expert_capacity_evidence_velocity_117' + (':passed' if allowed else ':blocked')

def guard_evidence_strength_benefit_confidence_118(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('benefit_confidence', 0.0)
    floor = float(context.get('guard_evidence_strength_benefit_confidence_118_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('balloting')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_strength_benefit_confidence_118' + (':passed' if allowed else ':blocked')

def guard_conflict_count_exit_risk_119(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('exit_risk', 0.0)
    floor = float(context.get('guard_conflict_count_exit_risk_119_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('adopted')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_conflict_count_exit_risk_119' + (':passed' if allowed else ':blocked')

def guard_public_value_agenda_board_balance_120(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('agenda_board_balance', 0.0)
    floor = float(context.get('guard_public_value_agenda_board_balance_120_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reopened')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_agenda_board_balance_120' + (':passed' if allowed else ':blocked')

GUARDS: tuple[Callable[[DomainRecord, Mapping[str, Any]], tuple[bool, str]], ...] = (
    guard_working_group_match_fit_01,
    guard_issue_urgency_disclosure_quality_02,
    guard_evidence_maturity_pilot_feasibility_03,
    guard_deliberation_window_supplier_concentration_04,
    guard_resource_band_evidence_velocity_05,
    guard_risk_class_benefit_confidence_06,
    guard_regional_relevance_exit_risk_07,
    guard_dependency_count_agenda_board_balance_08,
    guard_expert_capacity_match_fit_09,
    guard_evidence_strength_disclosure_quality_10,
    guard_conflict_count_pilot_feasibility_11,
    guard_public_value_supplier_concentration_12,
    guard_working_group_evidence_velocity_13,
    guard_issue_urgency_benefit_confidence_14,
    guard_evidence_maturity_exit_risk_15,
    guard_deliberation_window_agenda_board_balance_16,
    guard_resource_band_match_fit_17,
    guard_risk_class_disclosure_quality_18,
    guard_regional_relevance_pilot_feasibility_19,
    guard_dependency_count_supplier_concentration_20,
    guard_expert_capacity_evidence_velocity_21,
    guard_evidence_strength_benefit_confidence_22,
    guard_conflict_count_exit_risk_23,
    guard_public_value_agenda_board_balance_24,
    guard_working_group_match_fit_25,
    guard_issue_urgency_disclosure_quality_26,
    guard_evidence_maturity_pilot_feasibility_27,
    guard_deliberation_window_supplier_concentration_28,
    guard_resource_band_evidence_velocity_29,
    guard_risk_class_benefit_confidence_30,
    guard_regional_relevance_exit_risk_31,
    guard_dependency_count_agenda_board_balance_32,
    guard_expert_capacity_match_fit_33,
    guard_evidence_strength_disclosure_quality_34,
    guard_conflict_count_pilot_feasibility_35,
    guard_public_value_supplier_concentration_36,
    guard_working_group_evidence_velocity_37,
    guard_issue_urgency_benefit_confidence_38,
    guard_evidence_maturity_exit_risk_39,
    guard_deliberation_window_agenda_board_balance_40,
    guard_resource_band_match_fit_41,
    guard_risk_class_disclosure_quality_42,
    guard_regional_relevance_pilot_feasibility_43,
    guard_dependency_count_supplier_concentration_44,
    guard_expert_capacity_evidence_velocity_45,
    guard_evidence_strength_benefit_confidence_46,
    guard_conflict_count_exit_risk_47,
    guard_public_value_agenda_board_balance_48,
    guard_working_group_match_fit_49,
    guard_issue_urgency_disclosure_quality_50,
    guard_evidence_maturity_pilot_feasibility_51,
    guard_deliberation_window_supplier_concentration_52,
    guard_resource_band_evidence_velocity_53,
    guard_risk_class_benefit_confidence_54,
    guard_regional_relevance_exit_risk_55,
    guard_dependency_count_agenda_board_balance_56,
    guard_expert_capacity_match_fit_57,
    guard_evidence_strength_disclosure_quality_58,
    guard_conflict_count_pilot_feasibility_59,
    guard_public_value_supplier_concentration_60,
    guard_working_group_evidence_velocity_61,
    guard_issue_urgency_benefit_confidence_62,
    guard_evidence_maturity_exit_risk_63,
    guard_deliberation_window_agenda_board_balance_64,
    guard_resource_band_match_fit_65,
    guard_risk_class_disclosure_quality_66,
    guard_regional_relevance_pilot_feasibility_67,
    guard_dependency_count_supplier_concentration_68,
    guard_expert_capacity_evidence_velocity_69,
    guard_evidence_strength_benefit_confidence_70,
    guard_conflict_count_exit_risk_71,
    guard_public_value_agenda_board_balance_72,
    guard_working_group_match_fit_73,
    guard_issue_urgency_disclosure_quality_74,
    guard_evidence_maturity_pilot_feasibility_75,
    guard_deliberation_window_supplier_concentration_76,
    guard_resource_band_evidence_velocity_77,
    guard_risk_class_benefit_confidence_78,
    guard_regional_relevance_exit_risk_79,
    guard_dependency_count_agenda_board_balance_80,
    guard_expert_capacity_match_fit_81,
    guard_evidence_strength_disclosure_quality_82,
    guard_conflict_count_pilot_feasibility_83,
    guard_public_value_supplier_concentration_84,
    guard_working_group_evidence_velocity_85,
    guard_issue_urgency_benefit_confidence_86,
    guard_evidence_maturity_exit_risk_87,
    guard_deliberation_window_agenda_board_balance_88,
    guard_resource_band_match_fit_89,
    guard_risk_class_disclosure_quality_90,
    guard_regional_relevance_pilot_feasibility_91,
    guard_dependency_count_supplier_concentration_92,
    guard_expert_capacity_evidence_velocity_93,
    guard_evidence_strength_benefit_confidence_94,
    guard_conflict_count_exit_risk_95,
    guard_public_value_agenda_board_balance_96,
    guard_working_group_match_fit_97,
    guard_issue_urgency_disclosure_quality_98,
    guard_evidence_maturity_pilot_feasibility_99,
    guard_deliberation_window_supplier_concentration_100,
    guard_resource_band_evidence_velocity_101,
    guard_risk_class_benefit_confidence_102,
    guard_regional_relevance_exit_risk_103,
    guard_dependency_count_agenda_board_balance_104,
    guard_expert_capacity_match_fit_105,
    guard_evidence_strength_disclosure_quality_106,
    guard_conflict_count_pilot_feasibility_107,
    guard_public_value_supplier_concentration_108,
    guard_working_group_evidence_velocity_109,
    guard_issue_urgency_benefit_confidence_110,
    guard_evidence_maturity_exit_risk_111,
    guard_deliberation_window_agenda_board_balance_112,
    guard_resource_band_match_fit_113,
    guard_risk_class_disclosure_quality_114,
    guard_regional_relevance_pilot_feasibility_115,
    guard_dependency_count_supplier_concentration_116,
    guard_expert_capacity_evidence_velocity_117,
    guard_evidence_strength_benefit_confidence_118,
    guard_conflict_count_exit_risk_119,
    guard_public_value_agenda_board_balance_120,
)

def guard_report(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = dict(context or {})
    context['_metrics'] = grouped_metrics(record, context)
    results = [guard(record, context) for guard in GUARDS]
    return {'passed': sum(item[0] for item in results), 'failed': sum(not item[0] for item in results),
            'messages': [item[1] for item in results]}

def decide(record: DomainRecord, context: Mapping[str, Any] | None = None) -> Decision:
    context = context or {}
    rules = evaluate(record, context)
    scorecard = record_score(record, context)
    guards = guard_report(record, context)
    effective_score = scorecard['score'] * 0.55 + float(context.get('domain_signal', 0.5)) * 0.45
    critical = sum(item.severity == 'critical' for item in rules)
    if context.get('domain_severity') == 'critical':
        outcome = 'hold'
    elif critical:
        outcome = 'hold'
    elif effective_score >= float(context.get('approve_threshold', 0.62)) and guards['passed'] >= guards['failed']:
        outcome = 'approve'
    elif effective_score >= float(context.get('review_threshold', 0.38)):
        outcome = 'review'
    else:
        outcome = 'reject'
    reasons = (f"score={scorecard['score']:.6f}", f"critical={critical}",
               f"guards={guards['passed']}/{guards['passed'] + guards['failed']}")
    return Decision(record.record_id, outcome, effective_score, reasons, rules, scorecard['metrics'])

def advance_for_outcome(record: DomainRecord, decision: Decision) -> DomainRecord:
    current = STATES.index(record.state)
    if decision.outcome == 'approve' and current + 1 < len(STATES):
        return record.with_state(STATES[current + 1])
    if decision.outcome == 'hold' and STATES[-1] != record.state:
        return record.with_state(STATES[-1])
    return record
