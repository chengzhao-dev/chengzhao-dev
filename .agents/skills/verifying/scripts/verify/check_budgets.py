#!/usr/bin/env python3
"""按 governing-agents 的篇幅预算表校验文档行数与 token 上限。

用法：
  python .agents/skills/verifying/scripts/verify/check_budgets.py

预算表是唯一事实来源：解析 `.agents/skills/governing-agents/SKILL.md` 中
「篇幅预算」一节的表格行，把每行的描述性路径解析成具体文件后逐个核对。
token 按「中文 1 字 ≈ 1 token、其他字符 4 个 ≈ 1 token」粗算。
输出一行一条结论，全部通过以 0 退出。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[5]
SKILL = ROOT / ".agents/skills/governing-agents/SKILL.md"


def token_estimate(text: str) -> int:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    other = len(text) - cjk
    return cjk + other // 4


def resolve(target: str) -> list[Path]:
    """把预算表的描述性路径解析成具体文件列表；解析不了就返回空列表。"""
    text = target.replace("`", "").strip()
    if "QUICK-REFERENCE" in text:
        return [ROOT / ".agents/QUICK-REFERENCE.md"]
    if text == "AGENTS.md":
        return [ROOT / "AGENTS.md"]
    if text == ".agents/README.md":
        return [ROOT / ".agents/README.md"]
    if "ARCHITECTURE.md" in text:
        return [ROOT / "ARCHITECTURE.md"]
    if "KNOWLEDGE.md" in text and "MEMORY.md" in text:
        return [ROOT / ".agents/knowledge/KNOWLEDGE.md", ROOT / ".agents/memory/MEMORY.md"]
    if "memory/domains" in text and "index" in text:
        return sorted((ROOT / ".agents/memory/domains").glob("*/index.md"))
    if "其他条目文件" in text:
        entries = [
            p for p in (ROOT / ".agents/knowledge").rglob("*.md") if p.name != "KNOWLEDGE.md"
        ]
        entries += [
            p
            for p in (ROOT / ".agents/memory").rglob("*.md")
            if p.name != "MEMORY.md" and p.name != "index.md"
        ]
        return sorted(entries)
    if "SKILL.md" in text:
        return sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    if ".agents/plan" in text:
        return sorted((ROOT / ".agents/plan").glob("*.md"))
    if "incidents/INDEX" in text:
        return [ROOT / ".agents/incidents/INDEX.md"]
    if "incidents" in text:
        return sorted((ROOT / ".agents/incidents").rglob("*.md"))
    if "references" in text:
        return sorted((ROOT / ".agents/skills").glob("*/references/*.md"))
    return []


def main() -> int:
    findings: list[str] = []

    rules_text = SKILL.read_text(encoding="utf-8")
    section = rules_text[rules_text.index("## 篇幅预算") : rules_text.index("行数含空行")]
    rules: list[tuple[str, int, int]] = []
    for line in section.splitlines():
        match = re.match(r"^\| (.+?) \| (\d+) \| (\d+) \|$", line.strip())
        if match:
            rules.append((match.group(1), int(match.group(2)), int(match.group(3))))

    if not rules:
        findings.append("预算表：未解析到任何规则，请检查 governing-agents 的表格格式")
        report(findings)
        return 1

    checked = 0
    for target, lines_limit, token_limit in rules:
        paths = resolve(target)
        if not paths:
            if ".agents/plan" in target or "incidents" in target:
                continue  # .agents/plan 与 incidents 目录允许暂空：没有文件时该规则静默跳过
            findings.append(f"预算表：规则「{target}」没有匹配到任何文件")
            continue
        for path in paths:
            checked += 1
            text = path.read_text(encoding="utf-8")
            lines = len(text.splitlines())
            tokens = token_estimate(text)
            rel = path.relative_to(ROOT)
            if lines > lines_limit:
                findings.append(f"{rel}：行数 {lines} 超过预算 {lines_limit}（{target}）")
            if tokens > token_limit:
                findings.append(f"{rel}：token 约 {tokens} 超过预算 {token_limit}（{target}）")

    if not checked:
        findings.append("预算表：没有任何文件被核对")
    report(findings)
    return 1 if findings else 0


def report(findings: list[str]) -> None:
    for item in findings:
        print(f"FAIL: {item}")
    print(f"{'PASS' if not findings else 'FAIL'}: {len(findings)} 处问题")


if __name__ == "__main__":
    raise SystemExit(main())
