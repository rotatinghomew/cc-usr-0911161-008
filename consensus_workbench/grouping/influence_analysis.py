"""分组对推进决定的实际影响分析。

影响判断建立在两层可复算的证据之上：

1. **实际决定层**：直接读取封存库中每条议题的真实 ``Decision``（outcome /
   score / critical 规则），这是秘书处当周真正做出的推进判断；
2. **反事实重放层**：用与生产管线完全相同的 ``derive_context`` /
   ``augment_context`` / ``decide`` 函数，在“剔除重复证据提交”的反事实记录集
   上重新决定，量化重复提交是否抬高了支持度、是否足以改变推进结果。

反事实重放只构造只读的内存记录视图，不写库、不覆盖任何封存结论。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from consensus_workbench.agenda.item_contract import Decision, DomainRecord
from consensus_workbench.ballots.vote_governance import decide
from consensus_workbench.consensus_signal.consensus_readiness import augment_context
from consensus_workbench.evidence.evidence_match import derive_context
from consensus_workbench.grouping.evidence_groups import (
    READINESS_BLOCK_FLOOR,
    ClassifiedRecord,
)

class _InMemoryRepository:
    """只实现重放所需只读接口的内存仓库（绝不落盘）。"""

    def __init__(self, records: Iterable[DomainRecord]):
        self._records = {record.record_id: record for record in records}

    def list_records(self, state: str | None = None) -> list[DomainRecord]:
        rows = sorted(self._records.values(), key=lambda item: item.record_id)
        return [row for row in rows if state is None or row.state == state]

    def get_record(self, record_id: str) -> DomainRecord | None:
        return self._records.get(record_id)


def replay_decisions(records: Iterable[DomainRecord]) -> dict[str, Decision]:
    """用生产决定函数在给定记录集上重放全部决定（只读、确定性）。"""
    repository = _InMemoryRepository(records)
    decisions: dict[str, Decision] = {}
    for stored in repository.list_records():
        context: dict[str, Any] = {}
        context.update(derive_context(stored, repository))
        context.update(augment_context(stored, repository))
        decisions[stored.record_id] = decide(stored, context)
    return decisions


def _decision_brief(decision: Decision) -> dict[str, Any]:
    critical = sum(rule.severity == "critical" for rule in decision.rule_results)
    return {"outcome": decision.outcome, "score": decision.score,
            "critical_rule_count": critical, "decision_id": decision.fingerprint}


@dataclass(frozen=True)
class CounterfactualResult:
    removed_duplicate_records: tuple[str, ...]
    retained_records: tuple[str, ...]
    baseline_outcomes: Mapping[str, str]
    counterfactual_outcomes: Mapping[str, str]
    changed_records: tuple[str, ...]
    any_outcome_changed: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "removed_duplicate_records": list(self.removed_duplicate_records),
            "retained_records": list(self.retained_records),
            "baseline_outcomes": dict(self.baseline_outcomes),
            "counterfactual_outcomes": dict(self.counterfactual_outcomes),
            "changed_records": list(self.changed_records),
            "any_outcome_changed": self.any_outcome_changed,
        }


def counterfactual_without_duplicates(
        records: Iterable[DomainRecord],
        classified: Iterable[ClassifiedRecord],
        baseline_decisions: Mapping[str, Decision]) -> CounterfactualResult:
    """剔除“重复证据”角色的提交后重放，与封存基线决定逐条对比。

    独立议题（每个证据签名的首次提交）全部保留；仅移除后续重复提交，
    模拟“重复提交不再抬高支持度”的反事实世界。
    """
    records_by_id = {record.record_id: record for record in records}
    duplicate_ids = tuple(sorted(item.record_id for item in classified
                                 if item.record_role == "duplicate_evidence"))
    retained = sorted(rid for rid in records_by_id if rid not in set(duplicate_ids))
    counterfactual = replay_decisions(records_by_id[rid] for rid in retained)

    baseline_outcomes = {rid: baseline_decisions[rid].outcome
                         for rid in sorted(baseline_decisions)}
    counterfactual_outcomes = {rid: decision.outcome
                               for rid, decision in sorted(counterfactual.items())}
    changed = tuple(sorted(rid for rid in counterfactual_outcomes
                           if rid in baseline_outcomes
                           and baseline_outcomes[rid] != counterfactual_outcomes[rid]))
    return CounterfactualResult(
        removed_duplicate_records=duplicate_ids,
        retained_records=tuple(retained),
        baseline_outcomes=baseline_outcomes,
        counterfactual_outcomes=counterfactual_outcomes,
        changed_records=changed,
        any_outcome_changed=bool(changed),
    )


def build_influence_report(
        report_body: Mapping[str, Any],
        records: Iterable[DomainRecord],
        baseline_decisions: Mapping[str, Decision]) -> dict[str, Any]:
    """判断每个工作组是否真正影响当周推进决定，并给出依据。

    影响类别（可多重命中，全部附证据）：

    * ``decision_critical``：该组存在容量临界议题（conflict_count ≥
      expert_capacity），生产管线据此给出 critical/hold，直接阻断推进；
    * ``readiness_blocked_hidden``：该组准备度最小值低于阻断线，分组信号已算出
      阻断但当前 ``decide`` 路径未消费——是被平均数遮住的潜在阻断点；
    * ``duplicate_inflation``：该组含重复证据提交，重复提交虚增了该组的
      submission_count 与议程板压力；
    * ``unassessable_absent``：缺席工作组，没有任何记录可供决定，无法影响本次
      推进，但压低工作组多样性、抬高供应商集中度权重。
    """
    records_by_id = {record.record_id: record for record in records}
    classified_by_id = {item["record_id"]: item for item in report_body["records"]}

    counterfactual = counterfactual_without_duplicates(
        records_by_id.values(),
        [ClassifiedRecord.from_dict(item) for item in report_body["records"]],
        baseline_decisions,
    )
    duplicate_set = set(counterfactual.removed_duplicate_records)

    group_influence: list[dict[str, Any]] = []
    for group in report_body["groups"]:
        members = group["members"]
        capacity_critical = group["capacity_critical_records"]
        readiness_blocked = group["readiness_blocked"]
        duplicate_members = [rid for rid in members if rid in duplicate_set]
        held_members = [rid for rid in members
                        if rid in baseline_decisions
                        and baseline_decisions[rid].outcome == "hold"]

        categories: list[str] = []
        evidence_notes: list[str] = []
        if capacity_critical:
            categories.append("decision_critical")
            evidence_notes.append(
                "capacity_critical_records=" + ",".join(capacity_critical)
                + " -> domain_severity=critical -> outcome=hold")
        if readiness_blocked:
            categories.append("readiness_blocked_hidden")
            evidence_notes.append(
                f"readiness_minimum={group['readiness_minimum']:.6f} < "
                f"{READINESS_BLOCK_FLOOR} but blocked_groups signal is not consumed "
                "by the decide() path")
        if duplicate_members:
            categories.append("duplicate_inflation")
            evidence_notes.append(
                "duplicate_evidence_records=" + ",".join(duplicate_members)
                + " inflate submission_count from "
                f"{group['unique_evidence_signatures']} unique evidence to "
                f"{group['submission_count']} submissions")

        member_decisions = {rid: _decision_brief(baseline_decisions[rid])
                            for rid in members if rid in baseline_decisions}
        group_influence.append({
            "working_group": group["working_group"],
            "present": True,
            "influence_categories": categories,
            "affects_advancement": bool(capacity_critical),
            "advancement_basis": (
                "holds its agenda items via critical capacity/conflict rules"
                if capacity_critical else
                "no member triggers a critical hold in the sealed decision"),
            "held_member_count": len(held_members),
            "member_decisions": member_decisions,
            "evidence_notes": evidence_notes,
        })

    absent_influence = [{
        "working_group": name,
        "present": False,
        "influence_categories": ["unassessable_absent"],
        "affects_advancement": False,
        "advancement_basis": "no records submitted; cannot enter the decision path",
        "held_member_count": 0,
        "member_decisions": {},
        "evidence_notes": [
            "absent from every record; excluded from readiness minima and reduces "
            "working_group_diversity, which raises supplier_concentration_weight for "
            "all present records"],
    } for name in report_body["absent_groups"]]

    decision_groups = [entry["working_group"] for entry in group_influence
                       if entry["affects_advancement"]]
    hidden_groups = [entry["working_group"] for entry in group_influence
                     if "readiness_blocked_hidden" in entry["influence_categories"]]
    inflated_groups = [entry["working_group"] for entry in group_influence
                       if "duplicate_inflation" in entry["influence_categories"]]

    return {
        "analysis_version": 1,
        "decision_path": "secretariat.Application.process -> derive_context + "
                         "augment_context -> vote_governance.decide",
        "baseline_outcome_counts": _outcome_counts(baseline_decisions),
        "groups_affecting_advancement": decision_groups,
        "groups_readiness_blocked_hidden": hidden_groups,
        "groups_with_duplicate_inflation": inflated_groups,
        "absent_groups_unassessable": report_body["absent_groups"],
        "counterfactual_dedup": counterfactual.as_dict(),
        "counterfactual_interpretation": (
            "outcome unchanged: duplicate submissions inflate support signals but do "
            "not change any sealed outcome in this run"
            if not counterfactual.any_outcome_changed else
            "outcome changed for the listed records when duplicate evidence is removed"
        ),
        "group_influence": group_influence + absent_influence,
    }


def _outcome_counts(decisions: Mapping[str, Decision]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for decision in decisions.values():
        counts[decision.outcome] = counts.get(decision.outcome, 0) + 1
    return dict(sorted(counts.items()))
