#!/usr/bin/env python3
"""注册表检索效果评测（一次性度量工具，不进 CI）。

用固定查询集测 registry.py search 的命中情况与耗时，并启发式估算
QUICK-REFERENCE.md / registry.json 的 token 开销，对照「盲读全部条目正文」
给出节省比例。结论打印到 stdout 并写入 temp/benchmark_registry.txt。

用法：python .agents/skills/governing-agents/scripts/registry_bench.py
Token 估算为启发式（CJK 约 1 token/字，连续 ASCII 约 4 字符/token），非精确值。
"""

from __future__ import annotations

import argparse
import io
import json
import math
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable, TypeVar

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry as reg  # noqa: E402

T = TypeVar("T")

# 正例：(查询词, 期望命中条目名子串)；反例：期望无结果。
CASES: list[tuple[str, str]] = [
    ("quarto", "maintaining-readme"),
    ("render", "maintaining-readme"),
    ("ffmpeg", "source-artifacts"),
    ("横幅", "designing-visuals"),
    ("色板", "bright-palette"),
    ("gitignore", "branches-workflows"),
    ("注释", "writing-chinese"),
    ("解释器", "local-env/python"),
    ("缓存", "stale-project-cache"),
    ("信任", "trust-tiers"),
]
NEGATIVES: list[str] = ["xyzzy", "区块链", "kubernetes-operator"]

SEARCH_RUNS = 50
SCAN_RUNS = 10


def estimate_tokens(text: str) -> int:
    """启发式 token 估算：CJK 约 1 token/字，其余按 4 字符/token。"""
    cjk = sum(
        1 for ch in text
        if "\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f"
        or "\uff00" <= ch <= "\uffef"
    )
    return cjk + math.ceil((len(text) - cjk) / 4)


def bench(fn: Callable[[], T], runs: int) -> tuple[T, float]:
    """执行 runs 次取平均耗时（ms），返回最后一次结果与平均耗时。"""
    result: T | None = None
    start = time.perf_counter()
    for _ in range(runs):
        result = fn()
    return result, (time.perf_counter() - start) * 1000 / runs


def run_search(*keywords: str) -> list[dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        reg.cmd_search(argparse.Namespace(keywords=list(keywords)))
    return buf.getvalue().splitlines()


def main() -> int:
    lines: list[str] = ["# 注册表检索效果评测", ""]

    # 1. 命中率
    top1 = any_hits = 0
    lines.append("## search 命中（top-1 = 首条即期望条目；any = 结果中含期望条目）")
    lines.append("")
    for keyword, expected in CASES:
        results = run_search(keyword)
        t1 = bool(results) and expected in results[0]
        anyhit = any(expected in r for r in results)
        top1 += t1
        any_hits += anyhit
        lines.append(f"- {keyword!r} → top-1 {'命中' if t1 else '未中'}，any {'命中' if anyhit else '未中'}"
                     f"（{len(results)} 条）")
    lines.append("")
    lines.append(f"正例：top-1 {top1}/{len(CASES)}，any {any_hits}/{len(CASES)}")
    neg_clean = sum(1 for kw in NEGATIVES if all("无匹配" in r for r in run_search(kw)))
    lines.append(f"反例：{neg_clean}/{len(NEGATIVES)} 正确返回无结果")
    lines.append("")

    # 2. 耗时：读 registry.json（现行 search）vs 全量重扫（旧实现）
    _, load_ms = bench(lambda: reg._load_registry(), SEARCH_RUNS)
    _, scan_ms = bench(reg.build_registry, SCAN_RUNS)
    lines.append("## 单次耗时（均值）")
    lines.append(f"- search（读 registry.json，现行）：{load_ms:.2f} ms")
    lines.append(f"- 全量重扫（旧实现每次 search 都做）：{scan_ms:.2f} ms")
    lines.append(f"- 提速：约 {scan_ms / max(load_ms, 0.01):.0f} 倍")
    lines.append("")

    # 3. token 开销
    entries = reg._load_registry()["entries"]
    quick_tokens = estimate_tokens(reg.QUICK_REF_PATH.read_text(encoding="utf-8"))
    registry_tokens = estimate_tokens(reg.REGISTRY_PATH.read_text(encoding="utf-8"))
    body_tokens = 0
    per_entry: list[int] = []
    for entry in entries:
        path = reg.ROOT / entry["path"]
        if path.is_file():
            tokens = estimate_tokens(path.read_text(encoding="utf-8"))
            body_tokens += tokens
            per_entry.append(tokens)
    avg_entry = sum(per_entry) / len(per_entry)
    lines.append("## token 开销（启发式估算，非精确）")
    lines.append(f"- QUICK-REFERENCE.md：约 {quick_tokens} tokens（常驻检索入口）")
    lines.append(f"- registry.json：约 {registry_tokens} tokens（数据文件，agent 一般不整读）")
    lines.append(f"- 全部 {len(entries)} 个条目正文合计：约 {body_tokens} tokens")
    lines.append(f"- 条目正文均值：约 {avg_entry:.0f} tokens")
    savings = (1 - quick_tokens / body_tokens) * 100
    lines.append(f"- 速查表相对盲读全部正文：省约 {savings:.0f}% tokens")
    lines.append(f"- 典型流程（读速查表 + 命中 1 个条目）：约 {quick_tokens + avg_entry:.0f} tokens，"
                 f"相对盲读省约 {(1 - (quick_tokens + avg_entry) / body_tokens) * 100:.0f}%")
    lines.append("")
    lines.append("## 结论")
    lines.append(f"- 检索定位一次只需速查表（约 {quick_tokens} tokens）+ 目标正文"
                 f"（均值约 {avg_entry:.0f} tokens），显著优于盲读全部 {body_tokens} tokens。")
    lines.append("- search 已改为读 registry.json，粗筛成本可忽略；速查表负责语义细选，"
                 "search/lookup 负责粗筛与查找，二者互补。")

    report = "\n".join(lines) + "\n"
    print(report)
    out_dir = reg.ROOT / "temp"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "benchmark_registry.txt"
    out_path.write_text(report, encoding="utf-8")
    print(f"报告已写入 {out_path.relative_to(reg.ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
