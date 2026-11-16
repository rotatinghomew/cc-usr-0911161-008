"""按工作组划分的证据分组与议题分类。

设计原则：
* 所有输入均为既有 ``DomainRecord``（含 record_id / version / state /
  fingerprint），输出逐条回链到这些原始记录与版本，不引入不可追溯的外部输入。
* 证据签名只取证据关联字段（成熟度、强度、区域相关性），完全相同的签名视为
  同一证据的重复提交；容量、冲突、紧迫度等需求侧字段不参与签名，避免把
  “不同议题引用同一证据”误判成同一议题。
* 缺席分组依据明确的期望名册（默认 8 个工作组，与
  ``agenda_board_pressure`` 的多样性分母一致），名册可显式覆盖并写入报告。
"""

from __future__ import annotations

from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from consensus_workbench.agenda.item_contract import DomainRecord, stable_hash
from consensus_workbench.consensus_signal.consensus_readiness import (
    consensus_readiness,
    number,
    ratio,
)

#: 构成证据关联的字段：三元组完全一致才认定为重复证据。
EVIDENCE_SIGNATURE_FIELDS: tuple[str, ...] = (
    "evidence_maturity",
    "evidence_strength",
    "regional_relevance",
)

#: 分组准备度阻断线，与 consensus_signal.peer_distribution 的 <0.35 口径一致。
READINESS_BLOCK_FLOOR: float = 0.35

#: 默认期望工作组名册大小（与 agenda_board_pressure 的 8.0 多样性分母对齐）。
DEFAULT_ROSTER_SIZE = 8


def evidence_signature(payload: Mapping[str, Any]) -> str:
    """返回证据三元组的稳定签名。

    用与全局一致的 ``stable_hash``（规范化 JSON + sha256），保证同一证据在
    任意运行中得到同一签名，且可由原始字段独立复算核验。
    """
    body = {field: ratio(payload, field) for field in EVIDENCE_SIGNATURE_FIELDS}
    return stable_hash(body)


def expected_roster(records: Iterable[DomainRecord],
                    roster_size: int = DEFAULT_ROSTER_SIZE,
                    roster_override: Sequence[str] | None = None) -> list[str]:
    """确定期望工作组名册。

    显式 ``roster_override`` 优先；否则从实际记录的 ``working_group`` 标识符中
    解析数字后缀（如 ``working_group-3`` → 3），取 0..roster_size-1 补齐。
    推断规则随报告一起留存，保证名册来源可追溯。
    """
    if roster_override is not None:
        roster = [str(item).strip() for item in roster_override if str(item).strip()]
        if not roster:
            raise ValueError("roster_override must not be empty")
        if len(roster) != len(set(roster)):
            raise ValueError("roster_override contains duplicate working groups")
        return roster

    observed = {str(record.payload.get("working_group", "unknown"))
                for record in records}
    prefixes: set[str] = set()
    indexes: set[int] = set()
    for name in observed:
        if "-" in name:
            head, _, tail = name.rpartition("-")
            if tail.isdigit():
                prefixes.add(head)
                indexes.add(int(tail))
    if prefixes and indexes:
        prefix = sorted(prefixes)[0]
        width = max(1, len(str(max(indexes, default=0))))
        return [f"{prefix}-{index:0{width}d}" for index in range(roster_size)]
    # 无法解析数字后缀时，名册退化为实际出现过的工作组（此时无缺席可判定）。
    return sorted(observed)


@dataclass(frozen=True)
class ClassifiedRecord:
    """单条议题的分类结果，字段全部可回链原始记录。"""

    record_id: str
    version: int
    state: str
    working_group: str
    fingerprint: str
    evidence_signature: str
    record_role: str  # "independent_issue" | "duplicate_evidence"
    duplicate_of: tuple[str, ...]
    readiness_score: float
    readiness_severity: str
    readiness_evidence: dict[str, Any]
    quorum_margin: float
    evidence_gap: bool  # 证据成熟度或强度低于该证据三元组整体水平的标记
    capacity_critical: bool  # conflict_count >= expert_capacity

    def as_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "version": self.version,
            "state": self.state,
            "working_group": self.working_group,
            "fingerprint": self.fingerprint,
            "evidence_signature": self.evidence_signature,
            "record_role": self.record_role,
            "duplicate_of": list(self.duplicate_of),
            "readiness_score": self.readiness_score,
            "readiness_severity": self.readiness_severity,
            "readiness_evidence": self.readiness_evidence,
            "quorum_margin": self.quorum_margin,
            "evidence_gap": self.evidence_gap,
            "capacity_critical": self.capacity_critical,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ClassifiedRecord":
        """从封存报告的记录条目还原分类对象（回链核验/反事实重放用）。"""
        return cls(
            record_id=value["record_id"], version=value["version"], state=value["state"],
            working_group=value["working_group"], fingerprint=value["fingerprint"],
            evidence_signature=value["evidence_signature"],
            record_role=value["record_role"],
            duplicate_of=tuple(value["duplicate_of"]),
            readiness_score=value["readiness_score"],
            readiness_severity=value["readiness_severity"],
            readiness_evidence=dict(value["readiness_evidence"]),
            quorum_margin=value["readiness_evidence"]["quorum_margin"],
            evidence_gap=value["evidence_gap"],
            capacity_critical=value["capacity_critical"])


def classify_records(records: Iterable[DomainRecord]) -> list[ClassifiedRecord]:
    """把每条议题分类为独立议题或重复证据。

    同一证据签名首次出现的记录为 ``independent_issue``，之后出现的为
    ``duplicate_evidence``，并在 ``duplicate_of`` 中记录同签名的全部其他
    record_id（按 record_id 排序，保证确定性）。
    """
    ordered = sorted(records, key=lambda item: item.record_id)
    signatures: dict[str, list[str]] = defaultdict(list)
    for record in ordered:
        signatures[evidence_signature(record.payload)].append(record.record_id)

    classified: list[ClassifiedRecord] = []
    seen: set[str] = set()
    for record in ordered:
        signature = evidence_signature(record.payload)
        peers = sorted(peer for peer in signatures[signature]
                       if peer != record.record_id)
        role = "independent_issue" if signature not in seen else "duplicate_evidence"
        seen.add(signature)

        signal = consensus_readiness(record.payload)
        capacity = max(0.0, number(record.payload, "expert_capacity"))
        conflicts = max(0.0, number(record.payload, "conflict_count"))
        maturity = ratio(record.payload, "evidence_maturity")
        strength = ratio(record.payload, "evidence_strength")
        classified.append(ClassifiedRecord(
            record_id=record.record_id,
            version=record.version,
            state=record.state,
            working_group=str(record.payload.get("working_group", "unknown")),
            fingerprint=record.fingerprint,
            evidence_signature=signature,
            record_role=role,
            duplicate_of=tuple(peers),
            readiness_score=signal.score,
            readiness_severity=signal.severity,
            readiness_evidence=dict(signal.evidence),
            quorum_margin=signal.evidence["quorum_margin"],
            evidence_gap=min(maturity, strength) < READINESS_BLOCK_FLOOR,
            capacity_critical=conflicts >= capacity or capacity <= 0.0,
        ))
    return classified


def build_group_report(records: Iterable[DomainRecord],
                       roster_size: int = DEFAULT_ROSTER_SIZE,
                       roster_override: Sequence[str] | None = None) -> dict[str, Any]:
    """生成完整的分组共识分析报告主体（不含封存元数据）。

    报告分三部分：
    ``records``     —— 逐条分类结果，回链 record_id/version/fingerprint；
    ``groups``      —— 每个出席工作组的聚合判断（准备度最小值而非平均数、
                       重复证据、证据缺口、容量临界、阻断状态）；
    ``absent_groups`` —— 期望名册中没有任何提交、因此无法评估的工作组。
    """
    ordered = sorted(records, key=lambda item: item.record_id)
    roster = expected_roster(ordered, roster_size, roster_override)
    classified = classify_records(ordered)

    by_group: dict[str, list[ClassifiedRecord]] = defaultdict(list)
    for item in classified:
        by_group[item.working_group].append(item)

    groups: list[dict[str, Any]] = []
    for working_group in sorted(by_group):
        members = by_group[working_group]
        readiness = [item.readiness_score for item in members]
        minimum = min(readiness)
        group: dict[str, Any] = {
            "working_group": working_group,
            "present": True,
            "submission_count": len(members),
            "unique_evidence_signatures": len({item.evidence_signature for item in members}),
            "members": [item.record_id for item in members],
            "independent_issues": [item.record_id for item in members
                                   if item.record_role == "independent_issue"],
            "duplicate_evidence": [
                {"record_id": item.record_id, "duplicate_of": list(item.duplicate_of),
                 "evidence_signature": item.evidence_signature}
                for item in members if item.record_role == "duplicate_evidence"
            ],
            "readiness_minimum": minimum,
            "readiness_scores": {item.record_id: item.readiness_score for item in members},
            "readiness_blocked": minimum < READINESS_BLOCK_FLOOR,
            "evidence_gap_records": [item.record_id for item in members if item.evidence_gap],
            "capacity_critical_records": [item.record_id for item in members
                                          if item.capacity_critical],
            "record_refs": [
                {"record_id": item.record_id, "version": item.version,
                 "state": item.state, "fingerprint": item.fingerprint}
                for item in members
            ],
        }
        groups.append(group)

    present = set(by_group)
    absent = [name for name in roster if name not in present]

    signature_owners: dict[str, list[str]] = defaultdict(list)
    for item in classified:
        signature_owners[item.evidence_signature].append(item.record_id)
    duplicate_clusters = [
        {"evidence_signature": signature,
         "record_ids": sorted(record_ids),
         "working_groups": sorted({next(item.working_group for item in classified
                                        if item.record_id == rid) for rid in record_ids}),
         "submission_count": len(record_ids)}
        for signature, record_ids in sorted(signature_owners.items())
        if len(record_ids) > 1
    ]

    return {
        "analysis_version": 1,
        "roster": roster,
        "roster_source": "override" if roster_override is not None else "inferred",
        "roster_size_parameter": roster_size,
        "record_count": len(classified),
        "independent_issue_count": sum(item.record_role == "independent_issue"
                                       for item in classified),
        "duplicate_evidence_count": sum(item.record_role == "duplicate_evidence"
                                        for item in classified),
        "present_group_count": len(present),
        "absent_group_count": len(absent),
        "absent_groups": absent,
        "readiness_block_floor": READINESS_BLOCK_FLOOR,
        "evidence_signature_fields": list(EVIDENCE_SIGNATURE_FIELDS),
        "duplicate_clusters": duplicate_clusters,
        "records": [item.as_dict() for item in classified],
        "groups": groups,
    }


def fingerprint_index(report_body: Mapping[str, Any]) -> "OrderedDict[str, dict[str, Any]]":
    """报告主体内 record_id → 版本/指纹 的索引，供封存核验使用。"""
    index: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
    for ref_group in report_body["groups"]:
        for ref in ref_group["record_refs"]:
            index[ref["record_id"]] = ref
    return index
