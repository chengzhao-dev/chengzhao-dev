#!/usr/bin/env python3
"""chengzhao-dev 的统一检索协议适配器。

默认查询本仓库生成的 registry；传入 --corpus-root 时可对同一份 Markdown 语料
建立临时的条目级定位视图，用于与内容级检索器做公平对照。不会修改 registry。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXCLUDE = {".git", ".quarto", "_book", "build", "temp", "node_modules", ".cache", ".tmp"}


def title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def docs(root: Path):
    for path in sorted(root.rglob("*.md")):
        if set(path.relative_to(root).parts) & EXCLUDE:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        yield path, text


def search(query: str, root: Path, repository: str, top_k: int) -> dict:
    # 条目级路由基线：先按完整查询词命中，再按中文二元组补充，
    # 结果粒度仍是文件，不把它标记成 Parent/Child 语义召回。
    terms = [term.casefold() for term in re.findall(r"[\w一-龥-]{2,}", query)]
    bigrams = [query[index:index + 2].casefold() for index in range(max(0, len(query) - 1))]
    ranked = []
    for path, text in docs(root):
        haystack = (title(text, path.stem) + " " + text).casefold()
        score = sum(haystack.count(term) for term in terms)
        if not score:
            score = sum(haystack.count(term) for term in bigrams)
        if score:
            ranked.append((score, path, text))
    ranked.sort(key=lambda row: (-row[0], row[1].as_posix()))
    results = []
    for rank, (score, path, text) in enumerate(ranked[:max(1, top_k)], 1):
        rel = path.relative_to(ROOT if ROOT in path.parents else root).as_posix()
        results.append({
            "repository": repository,
            "id": rel,
            "kind": "knowledge" if "/knowledge/" in ("/" + rel) else "resource",
            "path": rel,
            "title": title(text, path.stem),
            "heading_path": title(text, path.stem),
            "score": score,
            "match_type": ["keyword"],
            "content": None,
            "source": {"path": rel},
            "updated": "",
            "status": "active",
            "rank": rank,
        })
    return {"request": {"repository": repository, "query": query, "top_k": top_k},
            "results": results, "mode": "entry-routing"}


def main() -> int:
    parser = argparse.ArgumentParser(description="统一检索响应适配器")
    parser.add_argument("query")
    parser.add_argument("--corpus-root", default=".agents")
    parser.add_argument("--repository", default="chengzhao-dev")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    root = Path(args.corpus_root).resolve()
    if not root.is_dir():
        raise SystemExit(f"corpus root not found: {root}")
    print(json.dumps(search(args.query, root, args.repository, args.top_k), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
