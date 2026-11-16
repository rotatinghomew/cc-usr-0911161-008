多边人工智能专家工作组共识编排台

运行验收：
python3 -m consensus_workbench run --fixture fixtures/acceptance.json --database /tmp/consensus_workbench.sqlite3 --output /tmp/consensus_workbench-output

核验：
python3 -m consensus_workbench verify --database /tmp/consensus_workbench.sqlite3 --output /tmp/consensus_workbench-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.consensus_signal.test_consensus_readiness -v

构建检查：
python3 -m compileall -q consensus_workbench tests
