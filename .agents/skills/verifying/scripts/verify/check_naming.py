#!/usr/bin/env python3
"""校验仓库命名、根目录白名单与技能 frontmatter 是否符合 governing-agents 规范。

用法：
  python .agents/skills/verifying/scripts/verify/check_naming.py

检查项：技能目录名与 SKILL.md 的 name 一致；Python 脚本模块名 snake_case；
文件与目录名不含连续连字符与模糊名称（utils、misc、temp、new、final）；
根目录顶层条目必须落在 structure.md 2.4 的封闭白名单内。
输出一行一条结论，全部通过以 0 退出。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
BANNED = {"utils", "misc", "temp", "new", "final"}
SNAKE = re.compile(r"^[a-z][a-z0-9_]*\.py$")

# 根目录封闭白名单（structure.md 2.4）：入口文件 + Quarto/公开面必需项。
# IGNORED_ROOT_ENTRIES 是被 .gitignore 忽略的本机条目，存在不算违规。
ROOT_ALLOWLIST = {
    "AGENTS.md",
    "README.md",
    "ARCHITECTURE.md",
    "LICENSE",
    ".gitattributes",
    ".gitignore",
    "index.qmd",
    "_quarto.yml",
    "_templates",
    "config.toml",
    "content",
    "assets",
    ".agents",
    ".github",
}
IGNORED_ROOT_ENTRIES = {"temp", ".quarto", ".zcode", ".zcodeignore", ".git"}


def main() -> int:
    findings: list[str] = []

    for skill_dir in sorted((ROOT / ".agents/skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            findings.append(f".agents/skills/{skill_dir.name}：缺少 SKILL.md")
            continue
        front = skill_md.read_text(encoding="utf-8").split("---")[1]
        name = re.search(r"^name:\s*(\S+)", front, re.M)
        if not name or name.group(1) != skill_dir.name:
            findings.append(f".agents/skills/{skill_dir.name}：目录名与 frontmatter name 不一致")

    for skill_dir in sorted((ROOT / ".agents/skills").iterdir()):
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.is_dir():
            continue
        for path in sorted(scripts_dir.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or "tool-cache" in path.parts:
                continue
            rel = path.relative_to(ROOT)
            if "--" in path.name:
                findings.append(f"{rel}：文件名含连续连字符")
            if path.suffix == ".py" and not SNAKE.match(path.name):
                findings.append(f"{rel}：Python 模块名不是 snake_case")
            if path.stem.lower() in BANNED:
                findings.append(f"{rel}：使用了模糊名称 {path.stem}")

    for path in sorted(ROOT.iterdir()):
        if path.is_dir() and path.stem.lower() in BANNED and path.name != "temp":
            findings.append(f"{path.name}/：目录名属于模糊名称")
        if path.name not in ROOT_ALLOWLIST and path.name not in IGNORED_ROOT_ENTRIES:
            kind = "目录" if path.is_dir() else "文件"
            findings.append(
                f"{path.name}：根目录白名单之外的{kind}"
                "（计划/审计类文档放 .agents/plan/，一次性草稿放 temp/，"
                "新常驻项需先更新 structure.md 2.4 与本白名单）"
            )

    report(findings)
    return 1 if findings else 0


def report(findings: list[str]) -> None:
    for item in findings:
        print(f"FAIL: {item}")
    print(f"{'PASS' if not findings else 'FAIL'}: {len(findings)} 处问题")


if __name__ == "__main__":
    raise SystemExit(main())
