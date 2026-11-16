"""分组共识分析与封存。

本包在既有议程记录、工作组、证据关联与状态判断之上，提供可追溯的分组共识
分析，明确区分独立议题、重复证据与缺席分组，并把结论封存为只追加、带哈希链
的报告，使后续补录无法无声改变先前已封存的结论。
"""

from consensus_workbench.grouping.evidence_groups import (
    EVIDENCE_SIGNATURE_FIELDS,
    READINESS_BLOCK_FLOOR,
    classify_records,
    build_group_report,
    expected_roster,
    evidence_signature,
)
from consensus_workbench.grouping.sealed_report import (
    ANALYSIS_VERSION,
    build_analysis,
    seal_analysis,
    verify_sealed_analysis,
    verify_analysis_index,
)

__all__ = [
    "ANALYSIS_VERSION",
    "EVIDENCE_SIGNATURE_FIELDS",
    "READINESS_BLOCK_FLOOR",
    "build_analysis",
    "build_group_report",
    "classify_records",
    "evidence_signature",
    "expected_roster",
    "seal_analysis",
    "verify_analysis_index",
    "verify_sealed_analysis",
]
