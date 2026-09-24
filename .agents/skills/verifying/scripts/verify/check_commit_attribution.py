#!/usr/bin/env python3
"""校验 git 历史中不含 Cursor 归属，避免 cursoragent 出现在 GitHub Contributors。

用法：
  python .agents/skills/verifying/scripts/verify/check_commit_attribution.py

扫描所有本地引用的提交信息与作者/提交者身份，命中 `cursoragent@cursor.com`
或作者名 `Cursor Agent` 时逐条列出并退出 1。只用标准库，不改动仓库。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 记录用 \x1e 分隔、字段用 \x1f 分隔，避免提交信息里的换行干扰解析。
LOG_FORMAT = "%H%x1f%an%x1f%ae%x1f%cn%x1f%ce%x1f%B%x1e"

FORBIDDEN_EMAIL_DOMAIN = "@cursor.com"
FORBIDDEN_NAMES = {"cursor", "cursor agent"}


def scan_history() -> list[str]:
    result = subprocess.run(
        ["git", "log", "--all", f"--format={LOG_FORMAT}"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "LC_ALL": "C.UTF-8"},
    )
    if result.returncode != 0:
        return []

    problems: list[str] = []
    for record in result.stdout.split("\x1e"):
        if not record.strip():
            continue
        sha, author_name, author_email, committer_name, committer_email, message = (
            record.split("\x1f", 5)
        )
        short = sha[:7]
        for role, name, email in (
            ("author", author_name, author_email),
            ("committer", committer_name, committer_email),
        ):
            if email.strip().lower().endswith(FORBIDDEN_EMAIL_DOMAIN):
                problems.append(f"{short} 的 {role} 身份是 Cursor：{name} <{email.strip()}>")
            elif name.strip().lower() in FORBIDDEN_NAMES:
                problems.append(f"{short} 的 {role} 名称是 Cursor：{name} <{email.strip()}>")
        for line in message.splitlines():
            lowered = line.strip().lower()
            if lowered.startswith("co-authored-by:") and (
                FORBIDDEN_EMAIL_DOMAIN in lowered or "cursor" in lowered
            ):
                problems.append(f"{short} 的提交信息含 Cursor 共著 trailer：{line.strip()}")
    return problems


def main() -> int:
    problems = scan_history()
    for item in problems:
        print(f"FAIL: {item}")
    if problems:
        print(f"FAIL: {len(problems)} 处 Cursor 归属；按 memory 的 cursor-attribution 条目清理")
        return 1
    print("PASS: git 历史中无 Cursor 归属")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())