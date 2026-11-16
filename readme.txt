多边人工智能专家工作组共识编排台

运行验收：
python3 -m consensus_workbench run --fixture fixtures/acceptance.json --database /tmp/consensus_workbench.sqlite3 --output /tmp/consensus_workbench-output

核验：
python3 -m consensus_workbench verify --database /tmp/consensus_workbench.sqlite3 --output /tmp/consensus_workbench-output

分组共识分析（基于已封存记录与决定，只追加封存，不改动历史结论）：
python3 -m consensus_workbench analyze --database /tmp/consensus_workbench.sqlite3 --analysis-dir /tmp/consensus_workbench-analysis

带分析回链与哈希链的完整核验（链/结果包/分析任一被篡改即返回非零）：
python3 -m consensus_workbench verify --database /tmp/consensus_workbench.sqlite3 --output /tmp/consensus_workbench-output --analysis-dir /tmp/consensus_workbench-analysis

可选：显式工作组名册（默认按 working_group-N 推断 8 个，缺席即无法评估）：
python3 -m consensus_workbench analyze --database /tmp/consensus_workbench.sqlite3 --analysis-dir /tmp/consensus_workbench-analysis --roster alpha beta gamma

分析口径（consensus_workbench/grouping/）：
- 证据签名 = sha256(规范化的 evidence_maturity/evidence_strength/regional_relevance)，
  三元组完全一致才认定为重复证据；容量、冲突、紧迫度等需求侧字段不参与签名。
- 每条议题分类为 independent_issue（签名首次出现）或 duplicate_evidence（后续重复提交）。
- 工作组准备度取组内最小值（而非平均数），低于 0.35 标记 readiness_blocked，
  暴露被平均数遮住的证据不足分组；conflict_count >= expert_capacity 标记容量临界。
- 影响判断含两层证据：封存库中的真实决定，以及“剔除重复提交后重放 decide()”的
  反事实结果（只读内存重放，不写库）。
- 缺席工作组（默认 working_group-5/6/7）记为 unassessable_absent，不计入支持度。

封存与补录语义：
- 报告主体不含时间戳，body_hash 为确定性 sha256；时间戳仅在外层封皮。
- analysis-index.json 为哈希链，新分析只追加、延长链，永不覆盖旧报告。
- 补录产生新版本后再次 analyze 会追加新报告；对旧报告做回链核验会显式报出
  指纹/版本分歧，而不会让先前已封存的结论无声改变。

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.consensus_signal.test_consensus_readiness -v
python3 -m unittest tests.grouping.test_evidence_groups tests.grouping.test_influence_analysis tests.grouping.test_sealed_report -v

构建检查：
python3 -m compileall -q consensus_workbench tests
