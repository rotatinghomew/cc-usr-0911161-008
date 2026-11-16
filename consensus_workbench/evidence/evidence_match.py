from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from consensus_workbench.agenda.item_contract import DomainRecord, bounded, finite_number, normalized_text


@dataclass(frozen=True)
class MatchEdge:
    demand_id: str
    supplier_id: str
    fit: float
    conflicts: tuple[str, ...]
    evidence: tuple[str, ...]


def demand_vector(record: DomainRecord) -> dict[str, float]:
    payload = record.payload
    return {"urgency": bounded(finite_number(payload.get("issue_urgency", 0.0)) / 10.0),
            "maturity": bounded(finite_number(payload.get("evidence_maturity", 0.0))),
            "regional_relevance": bounded(finite_number(payload.get("regional_relevance", 0.0))),
            "risk": bounded(finite_number(payload.get("risk_class", 0.0)) / 10.0)}


def supplier_vector(record: DomainRecord) -> dict[str, float]:
    payload = record.payload
    return {"capacity": bounded(finite_number(payload.get("expert_capacity", 0.0))),
            "evidence": bounded(finite_number(payload.get("evidence_strength", 0.0))),
            "independence": bounded(1.0 - finite_number(payload.get("conflict_count", 0.0)) / 10.0),
            "public_value": bounded(finite_number(payload.get("public_value", 0.0)))}


def match(record: DomainRecord, supplier_id: str, supplier: Mapping[str, float]) -> MatchEdge:
    issue = demand_vector(record)
    conflicts = []
    if supplier.get("capacity", 0.0) < issue["urgency"] * 0.7:
        conflicts.append("insufficient-expert-capacity")
    if supplier.get("evidence", 0.0) < issue["maturity"] * 0.5:
        conflicts.append("insufficient-evidence")
    if supplier.get("independence", 1.0) < 0.5:
        conflicts.append("unresolved-conflicts")
    fit = bounded((supplier.get("capacity", 0.0) + supplier.get("evidence", 0.0)
                   + supplier.get("independence", 1.0) + issue["regional_relevance"]) / 4.0
                  - len(conflicts) * 0.12)
    return MatchEdge(record.record_id, normalized_text(supplier_id), fit, tuple(conflicts),
                     tuple(name for name in ("evidence", "capacity", "independence")
                           if supplier.get(name, 0.0) >= 0.5))


def shortlist(record: DomainRecord, suppliers: Mapping[str, Mapping[str, float]], limit: int = 3) -> list[MatchEdge]:
    edges = [match(record, supplier_id, values) for supplier_id, values in suppliers.items()]
    return sorted(edges, key=lambda edge: (-edge.fit, len(edge.conflicts), edge.supplier_id))[:max(1, limit)]


def agenda_board_pressure(records: Iterable[DomainRecord]) -> dict[str, float]:
    rows = list(records)
    working_groups = {normalized_text(row.payload.get("working_group", "unknown")) for row in rows}
    capacities = [supplier_vector(row)["capacity"] for row in rows]
    conflicts = [max(0.0, finite_number(row.payload.get("conflict_count", 0.0))) for row in rows]
    return {"working_group_diversity": bounded(len(working_groups) / 8.0),
            "capacity_mean": sum(capacities) / max(1, len(rows)),
            "conflict_pressure": bounded(sum(conflicts) / max(1, len(rows) * 5.0))}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    evidence = supplier_vector(record)
    edge = match(record, str(record.payload.get("working_group", "unknown")), evidence)
    pressure = agenda_board_pressure(repository.list_records() or [record])
    return {"match_fit_weight": 0.6 + edge.fit * 0.6,
            "disclosure_quality_weight": 0.6 + evidence["evidence"] * 0.5,
            "pilot_feasibility_weight": 0.7 + evidence["capacity"] * 0.4,
            "supplier_concentration_weight": 1.1 - pressure["working_group_diversity"] * 0.3,
            "exit_risk_weight": 0.7 + pressure["conflict_pressure"] * 0.7}
