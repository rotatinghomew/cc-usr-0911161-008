from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class DomainSignal:
    code: str
    score: float
    severity: str
    evidence: dict[str, Any]

def number(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = float(payload.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if value != value or value in (float('inf'), float('-inf')) else value

def ratio(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    value = number(payload, key, default)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def consensus_readiness(payload: Mapping[str, Any]) -> DomainSignal:
    maturity = ratio(payload, 'evidence_maturity')
    strength = ratio(payload, 'evidence_strength')
    relevance = ratio(payload, 'regional_relevance')
    capacity = max(0.0, number(payload, 'expert_capacity'))
    dependencies = max(0.0, number(payload, 'dependency_count'))
    conflicts = max(0.0, number(payload, 'conflict_count'))
    window = max(1.0, number(payload, 'deliberation_window', 1.0))
    risk = min(1.0, number(payload, 'risk_class') / 5.0)
    quorum_margin = clamp((capacity-conflicts)/max(1.0, capacity))
    dependency_fit = clamp(1.0-dependencies/max(1.0, window))
    score = clamp(maturity*0.24 + strength*0.22 + relevance*0.12 + quorum_margin*0.2 + dependency_fit*0.12 + (1-risk)*0.1)
    severity = 'critical' if conflicts >= capacity or capacity <= 0 else 'warning' if dependency_fit < 0.4 else 'info'
    return DomainSignal('consensus_readiness', score, severity, {'quorum_margin': quorum_margin, 'dependency_fit': dependency_fit, 'conflicts': conflicts, 'capacity': capacity})

def peer_distribution(records: Iterable[Any], group_field: str = 'working_group') -> dict[str, Any]:
    readiness = {}
    for record in records:
        payload = getattr(record,'payload',record); readiness.setdefault(str(payload.get(group_field,'unknown')),[]).append(consensus_readiness(payload).score)
    minimums = {k:min(v) for k,v in readiness.items()}
    return {'working_groups': minimums, 'blocked_groups': sum(v < 0.35 for v in minimums.values()), 'count': sum(len(v) for v in readiness.values())}

def augment_context(record: Any, repository: Any) -> dict[str, Any]:
    signal = consensus_readiness(record.payload); peers = peer_distribution(repository.list_records())
    return {'domain_signal': signal.score, 'domain_severity': signal.severity, 'blocked_groups': peers['blocked_groups'], 'peer_count': peers['count']}
