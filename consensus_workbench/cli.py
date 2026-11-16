from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from consensus_workbench.secretariat import Application, analyze, run, verify


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog='consensus_workbench', description='多边人工智能专家工作组共识编排台')
    cli = root.add_subparsers(dest="command", required=True)
    execute = cli.add_parser("run")
    execute.add_argument("--fixture", required=True)
    execute.add_argument("--database", required=True)
    execute.add_argument("--output", required=True)
    check = cli.add_parser("verify")
    check.add_argument("--database", required=True)
    check.add_argument("--output", required=True)
    check.add_argument("--analysis-dir", default=None,
                       help="可选：同时核验该目录下封存的分组共识分析哈希链与回链")
    group = cli.add_parser("analyze",
                           help="基于已封存记录与决定生成分组共识分析并只追加封存")
    group.add_argument("--database", required=True)
    group.add_argument("--analysis-dir", required=True)
    group.add_argument("--roster-size", type=int, default=8)
    group.add_argument("--roster", nargs="*", default=None,
                       help="可选：显式工作组名册，覆盖自动推断")
    inspect = cli.add_parser("inspect")
    inspect.add_argument("--database", required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "run":
        result = run(args.fixture, args.database, args.output)
    elif args.command == "verify":
        result = verify(args.database, args.output, args.analysis_dir)
    elif args.command == "analyze":
        result = analyze(args.database, args.analysis_dir,
                         roster_size=args.roster_size, roster_override=args.roster)
    else:
        result = Application(args.database).inspect()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
