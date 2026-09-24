#!/usr/bin/env python3
"""本地静态校验的统一编排入口：依次调用各专门检查器并汇总退出码。

用法：
  python .agents/skills/verifying/scripts/verify/run_all.py [--skip-banner] [--verbose]

各检查器保持可单独运行；本脚本只负责顺序调用、透传输出，不做重复断言。
横幅媒体校验需要 Pillow 与横幅资源，无此环境时用 --skip-banner 跳过。
Quarto 渲染与渲染幂等检查不在这里，见 verifying 技能。
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# (显示名, 命令参数)；顺序即执行顺序，先便宜的静态检查后需要 Pillow 的媒体检查。
CHECKS = [
    ("命名规范", [".agents/skills/verifying/scripts/verify/check_naming.py"]),
    ("文档预算", [".agents/skills/verifying/scripts/verify/check_budgets.py"]),
    ("README 结构", [".agents/skills/verifying/scripts/verify/check_readme.py"]),
    ("提交归属", [".agents/skills/verifying/scripts/verify/check_commit_attribution.py"]),
    ("发布面静态", [".agents/skills/verifying/scripts/verify/check_publish.py"]),
    ("工作流与配置", [".agents/skills/verifying/scripts/verify/check_workflows.py"]),
    ("注册表零漂移", [".agents/skills/governing-agents/scripts/registry.py", "check"]),
    ("工作区审计", [".agents/skills/governing-agents/scripts/registry.py", "audit"]),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="依次运行全部静态校验器并汇总结果")
    parser.add_argument("--skip-banner", action="store_true",
                        help="跳过横幅媒体校验（需要 Pillow 与横幅资源）")
    args = parser.parse_args(argv)

    checks: list[tuple[str, list[str]]] = [
        (name, [sys.executable, *cmd]) for name, cmd in CHECKS
    ]
    if not args.skip_banner:
        checks.append(("横幅媒体", [sys.executable, ".agents/skills/designing-visuals/scripts/media/gen_banner.py", "--check"]))

    failed: list[str] = []
    for name, cmd in checks:
        result = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        output = (result.stdout + result.stderr).strip()
        if output:
            print(output)
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"{status}: {name}（退出码 {result.returncode}）")
        print()
        if result.returncode != 0:
            failed.append(name)

    if failed:
        print(f"未通过：{'、'.join(failed)}")
        return 1
    print(f"全部 {len(checks)} 项静态校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
