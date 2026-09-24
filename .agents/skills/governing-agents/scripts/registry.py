#!/usr/bin/env python3
"""agent 工作区注册表工具。

职责边界（Python 管确定性，LLM 管语义细选）：
- build   扫描 skills/knowledge/memory 与入口文档的 frontmatter，生成
          registry.json 与 QUICK-REFERENCE.md 两个生成物。
- check   断言磁盘上的生成物与重新扫描结果零漂移，不一致时逐条列出并退出 1。
- search  按关键词对注册表粗筛，输出「类型 路径 摘要」一行一条。
- lookup  注册表之外的查找能力：反向引用（哪些条目指向某文件，基于
          references 字段）与 .agents 及入口文档的全文搜索，默认两者都查。
- audit   死指针、孤儿文件、frontmatter 缺元数据，并委托 check_budgets
          复核篇幅预算。

frontmatter 元数据约定（挂在 metadata 下，见 Anthropic Agent Skills 的
metadata 字段定位）：
- metadata.triggers: 触发词列表，粗筛的主要依据
- metadata.paths:     glob 路径限定（借鉴 Cursor Auto Attached），可选
- metadata.summary:   一行摘要，缺省时回退 description 首句

注册表条目字段：type/path/name/title/summary/triggers/paths/lines/references，
skill 条目另有 files（技能目录内 git 跟踪文件数）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[4]
AGENTS_DIR = ROOT / ".agents"
REGISTRY_PATH = AGENTS_DIR / "registry.json"
QUICK_REF_PATH = AGENTS_DIR / "QUICK-REFERENCE.md"
BUDGET_CHECK = (
    ROOT / ".agents" / "skills" / "verifying" / "scripts" / "verify" / "check_budgets.py"
)

GENERATED_NOTE = (
    "<!-- 本文件由 .agents/skills/governing-agents/scripts/registry.py 生成，勿手改；"
    "手改会被 check 判为漂移。 -->"
)

# 入口文档无 frontmatter，元数据在此声明（唯一事实源，改这里即可）。
ENTRYPOINTS: tuple[dict[str, str], ...] = (
    {
        "path": "AGENTS.md",
        "name": "AGENTS",
        "summary": "硬性约束与执行原则，任务开始前必读",
        "triggers": "硬约束,红线,构建命令,执行原则",
    },
    {
        "path": "ARCHITECTURE.md",
        "name": "ARCHITECTURE",
        "summary": "项目结构、目录职责与常用流程图",
        "triggers": "结构,目录,流程图,新人入门",
    },
    {
        "path": ".agents/README.md",
        "name": "agents-workspace",
        "summary": "agent 工作区三区职责与归类判断规则",
        "triggers": "归类,放哪,工作区,技能规则",
    },
)

TYPE_LABELS = {"skill": "技能", "knowledge": "知识", "memory": "记忆", "entrypoint": "入口"}


def _flow_list(value: str) -> list[str]:
    items = [item.strip().strip("'\"") for item in value.strip().strip("[]").split(",")]
    return [item for item in items if item]


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """解析最小 YAML 子集：标量、一层嵌套、块列表与 flow 列表。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    data: dict[str, Any] = {}
    current: dict[str, Any] | None = None
    pending_list: str | None = None
    for line in lines[1:end]:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            body = line.strip()
            if pending_list and body.startswith("- "):
                current[pending_list].append(body[2:].strip().strip("'\""))
                continue
            if ":" in body and current is not None:
                key, _, value = body.partition(":")
                value = value.strip()
                if value.startswith("["):
                    current[key.strip()] = _flow_list(value)
                elif value == "":
                    current[key.strip()] = []
                    pending_list = key.strip()
                else:
                    current[key.strip()] = value.strip("'\"")
            continue
        pending_list = None
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith("["):
            data[key.strip()] = _flow_list(value)
        elif value == "":
            data[key.strip()] = {}
            current = data[key.strip()]
            pending_list = None
        else:
            data[key.strip()] = value.strip("'\"")
            current = None
    return data, "\n".join(lines[end + 1 :])


def extract_title(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def first_sentence(description: str) -> str:
    for sep in ("。", "；", ". "):
        idx = description.find(sep)
        if idx > 0:
            return description[: idx + len(sep)].rstrip()
    return description.strip()


def find_referenced_files(body: str, source: Path) -> list[str]:
    """从正文中提取指向仓库内文件的路径（相对仓库根或相对所在目录）。"""
    found: set[str] = set()
    pattern = re.compile(r"`([\w./-]+\.(?:md|py|json|toml|yml|yaml|lua|qmd|svg|webp|png))`")
    for token in pattern.findall(body):
        for base in (ROOT, source.parent):
            candidate = (base / token).resolve()
            if ROOT in candidate.parents or candidate == ROOT:
                if candidate.is_file():
                    found.add(candidate.relative_to(ROOT).as_posix())
                break
    for target in re.findall(r"\]\(([^)#\s]+)\)", body):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        candidate = (source.parent / target).resolve()
        if ROOT in candidate.parents and candidate.is_file():
            found.add(candidate.relative_to(ROOT).as_posix())
    return sorted(found)


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _tracked_files_under(directory: Path) -> set[str]:
    """返回 directory 下被 git 跟踪的文件（相对仓库根的 posix 路径）。

    技能 files 只统计入库文件：本机缓存、__pycache__ 等 gitignore 产物
    在 CI 干净检出里不存在，用 rglob 统计会与 CI 结果不一致。
    """
    prefix = directory.relative_to(ROOT).as_posix().rstrip("/") + "/"
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", prefix],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        return set()
    return {p for p in result.stdout.split("\0") if p.startswith(prefix)}


def scan_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def add_entry(etype: str, path: Path, name: str, meta: dict[str, Any],
                  title: str, body: str) -> None:
        md = meta.get("metadata", {}) if isinstance(meta.get("metadata"), dict) else {}
        triggers = md.get("triggers", [])
        if isinstance(triggers, str):
            triggers = _flow_list(triggers) if triggers.startswith("[") else [
                t.strip() for t in triggers.split(",") if t.strip()
            ]
        summary = md.get("summary") or first_sentence(meta.get("description", ""))
        paths_globs = md.get("paths", [])
        if isinstance(paths_globs, str):
            paths_globs = [paths_globs]
        entries.append({
            "type": etype,
            "path": path.relative_to(ROOT).as_posix(),
            "name": name,
            "title": title,
            "summary": summary,
            "triggers": triggers,
            "paths": paths_globs,
            "lines": len(text_lines(path)),
            "references": find_referenced_files(body, path),
        })

    for entry in ENTRYPOINTS:
        path = ROOT / entry["path"]
        if not path.is_file():
            entries.append({
                "type": "entrypoint", "path": entry["path"], "name": entry["name"],
                "title": entry["name"], "summary": entry["summary"],
                "triggers": [t.strip() for t in entry["triggers"].split(",")],
                "paths": [], "lines": 0, "references": [],
            })
            continue
        text = path.read_text(encoding="utf-8")
        add_entry("entrypoint", path, entry["name"], {}, entry["name"], text)
        entries[-1]["summary"] = entry["summary"]
        entries[-1]["triggers"] = [t.strip() for t in entry["triggers"].split(",")]

    skills_dir = AGENTS_DIR / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            meta, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            name = meta.get("name") or skill_dir.name
            add_entry("skill", skill_md, name, meta,
                      meta.get("name") or extract_title(body) or skill_dir.name, body)
            entries[-1]["files"] = len(_tracked_files_under(skill_dir))
            # 只计 git 跟踪文件：缓存、tool-cache 等本机产物不入库，
            # 统计必须与 CI 干净检出一致

    for kind, entry_md, index_summary in (
        ("knowledge", "KNOWLEDGE.md", "知识库索引：事实与参数"),
        ("memory", "MEMORY.md", "记忆索引：跨会话经验"),
    ):
        base = AGENTS_DIR / kind
        index = base / entry_md
        if index.is_file():
            meta, body = parse_frontmatter(index.read_text(encoding="utf-8"))
            add_entry("entrypoint", index, kind, meta, extract_title(body) or kind, body)
            entries[-1]["summary"] = entries[-1]["summary"] or index_summary
        for md_path in sorted(p for p in base.rglob("*.md") if p != index and p.name != "index.md"):
            meta, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
            add_entry(kind, md_path, meta.get("name") or md_path.stem, meta,
                      extract_title(body) or md_path.stem, body)
    return entries


def text_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def build_registry() -> dict[str, Any]:
    entries = scan_entries()
    return {
        "version": 1,
        "generated_by": ".agents/skills/governing-agents/scripts/registry.py build",
        "entries": entries,
    }


def _load_registry() -> dict[str, Any]:
    """读取磁盘 registry.json；缺失时回退 build_registry()，不自动重建。"""
    if REGISTRY_PATH.is_file():
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return build_registry()


def render_quick_reference(registry: dict[str, Any]) -> str:
    lines = [GENERATED_NOTE, "", "# 检索速查表", "",
             "先在本表定位条目再读正文；定位不到时运行",
             "`python .agents/skills/governing-agents/scripts/registry.py search <关键词>` 粗筛；",
             "查「哪些文档指向某文件」或搜正文用 "
             "`python .agents/skills/governing-agents/scripts/registry.py lookup <关键词>`。", ""]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in registry["entries"]:
        grouped.setdefault(entry["type"], []).append(entry)
    for etype in ("skill", "entrypoint", "knowledge", "memory"):
        items = grouped.get(etype, [])
        if not items:
            continue
        lines.append(f"## {TYPE_LABELS[etype]}（{etype}）")
        lines.append("")
        lines.append("| 名称 | 摘要 | 触发词 | 路径 |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for entry in items:
            triggers = "、".join(entry["triggers"]) or "—"
            summary = entry["summary"].replace("|", "\\|")
            lines.append(
                f"| {entry['name']} | {summary} | {triggers} | `{entry['path']}` |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def cmd_build(args: argparse.Namespace) -> int:
    registry = build_registry()
    REGISTRY_PATH.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    QUICK_REF_PATH.write_text(render_quick_reference(registry), encoding="utf-8")
    print(f"已写入 {REGISTRY_PATH.relative_to(ROOT).as_posix()} 与 "
          f"{QUICK_REF_PATH.relative_to(ROOT).as_posix()}，共 {len(registry['entries'])} 条目")
    return 0


def _diff_entries(built: list[dict[str, Any]], disk: list[dict[str, Any]]) -> list[str]:
    problems: list[str] = []
    built_by = {e["path"]: e for e in built}
    disk_by = {e["path"]: e for e in disk}
    for path in sorted(set(built_by) - set(disk_by)):
        problems.append(f"漂移：registry 缺少条目 {path}（重跑 build）")
    for path in sorted(set(disk_by) - set(built_by)):
        problems.append(f"漂移：registry 含已不存在的条目 {path}（重跑 build）")
    for path in sorted(set(built_by) & set(disk_by)):
        if built_by[path] != disk_by[path]:
            problems.append(f"漂移：条目元数据过期 {path}（重跑 build）")
    return problems


def cmd_check(args: argparse.Namespace) -> int:
    built = build_registry()
    problems: list[str] = []
    if not REGISTRY_PATH.is_file() or not QUICK_REF_PATH.is_file():
        problems.append("漂移：registry.json 或 QUICK-REFERENCE.md 不存在（重跑 build）")
    else:
        disk_registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        problems.extend(_diff_entries(built["entries"], disk_registry.get("entries", [])))
        disk_quick = QUICK_REF_PATH.read_text(encoding="utf-8")
        if disk_quick != render_quick_reference(built):
            problems.append("漂移：QUICK-REFERENCE.md 与扫描结果不一致（重跑 build）")
    for line in problems:
        print(line)
    if problems:
        return 1
    print(f"check 通过：registry 与 QUICK-REFERENCE 均为最新，共 {len(built['entries'])} 条目")
    return 0


def _entry_matches(entry: dict[str, Any], keyword: str) -> bool:
    haystack = " ".join([
        entry["name"], entry["title"], entry["summary"],
        " ".join(entry["triggers"]), entry["path"],
    ]).lower()
    return keyword.lower() in haystack


def cmd_search(args: argparse.Namespace) -> int:
    entries = _load_registry()["entries"]
    results = [
        e for e in entries
        if all(_entry_matches(e, kw) for kw in args.keywords)
    ]
    if not results:
        print("无匹配条目；建议换用更短或更泛的关键词，或运行 audit 排查")
        return 1
    for entry in results[:20]:
        label = TYPE_LABELS[entry["type"]]
        print(f"[{label}] {entry['path']} — {entry['summary']}")
    if len(results) > 20:
        print(f"（仅显示前 20 条，共 {len(results)} 条）")
    return 0


FULLTEXT_LIMIT = 40


def _iter_doc_files() -> list[Path]:
    """全文搜索范围：.agents 下全部 md 与根目录入口文档，排除生成物。"""
    files = [ROOT / "AGENTS.md", ROOT / "ARCHITECTURE.md"]
    files.extend(sorted(AGENTS_DIR.rglob("*.md")))
    return [p for p in files if p.is_file() and p.name != "QUICK-REFERENCE.md"]


def _lookup_backref(entries: list[dict[str, Any]], keyword: str) -> list[str]:
    """反向引用：输出 references 含该路径片段的条目，即「谁指向了它」。"""
    kw = keyword.lower()
    lines = []
    for entry in entries:
        hits = [ref for ref in entry.get("references", []) if kw in ref.lower()]
        if hits:
            label = TYPE_LABELS[entry["type"]]
            lines.append(f"[{label}] {entry['path']} → {'、'.join(hits)}")
    return lines


def _lookup_fulltext(keyword: str) -> list[str]:
    """全文搜索：文档正文行级大小写不敏感匹配，跳过代码块内示例。"""
    kw = keyword.lower()
    lines: list[str] = []
    for md_path in _iter_doc_files():
        in_fence = False
        for i, line in enumerate(md_path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or kw not in line.lower():
                continue
            rel = md_path.relative_to(ROOT).as_posix()
            lines.append(f"{rel}:{i}: {line.strip()}")
            if len(lines) >= FULLTEXT_LIMIT:
                lines.append(f"（达到 {FULLTEXT_LIMIT} 条上限，截断）")
                return lines
    return lines


def cmd_lookup(args: argparse.Namespace) -> int:
    found = False
    if not args.fulltext:
        hits = _lookup_backref(_load_registry()["entries"], args.keyword)
        if hits:
            found = True
            print("反向引用：")
            print("\n".join(hits))
    if not args.backref:
        hits = _lookup_fulltext(args.keyword)
        if hits:
            found = True
            if not args.fulltext and found:
                print()
            print("全文搜索：")
            print("\n".join(hits))
    if not found:
        print(f"lookup 无结果：{args.keyword}")
        return 1
    return 0


def _resolve_pointer(token: str, source: Path) -> Path | None:
    """把正文中的路径简写解析到唯一候选；解析不到返回 None。

    支持四类写法（与 structure.md 的目录约定一致）：
    - 仓库根相对：`.agents/skills/...`
    - 所在目录相对：技能内的 `references/naming.md`
    - 技能名简写：`maintaining-readme/references/...` → `.agents/skills/` 下
    - 工作区简写：`knowledge/<域>/...`、`memory/domains/...`、`incidents/...` → `.agents/` 下
    单段裸名（如 `SKILL.md`、`config.toml`）只按所在目录与仓库根解析，解析不到视为行文简写，不报死指针。
    """
    if token.startswith(("http://", "https://", "mailto:")) or token.endswith("registry.py"):
        return None
    bases = [ROOT, source.parent, source.parent.parent]
    first = token.split("/")[0]
    if (AGENTS_DIR / "skills" / first).is_dir():
        bases.append(AGENTS_DIR / "skills")
    if first == "references":
        # `references/xxx.md` 出现在技能根之外时，指技能内固定参考目录
        bases.extend(skill_dir for skill_dir in (AGENTS_DIR / "skills").iterdir()
                     if skill_dir.is_dir())
    if first in ("knowledge", "memory"):
        bases.append(AGENTS_DIR)
    if first == "incidents":
        bases.append(AGENTS_DIR)
    if (AGENTS_DIR / "knowledge" / first).is_dir():
        bases.append(AGENTS_DIR / "knowledge")
    if (AGENTS_DIR / "memory" / "domains" / first).is_dir():
        bases.append(AGENTS_DIR / "memory" / "domains")
    for base in bases:
        candidate = (base / token).resolve()
        if ROOT in candidate.parents and candidate.is_file():
            return candidate
    if "/" not in token:
        return None
    return (ROOT / token).resolve() if ROOT in (ROOT / token).resolve().parents else None


def cmd_audit(args: argparse.Namespace) -> int:
    problems: list[str] = []
    entries = build_registry()["entries"]
    registered = {e["path"] for e in entries}
    skill_dirs = {
        (AGENTS_DIR / "skills" / d.name).resolve()
        for d in (AGENTS_DIR / "skills").iterdir() if d.is_dir()
    } if (AGENTS_DIR / "skills").is_dir() else set()
    index_names = {"KNOWLEDGE.md", "MEMORY.md", "index.md"}

    for entry in entries:
        if entry["type"] == "entrypoint":
            continue
        path = ROOT / entry["path"]
        if path.name in index_names:
            continue  # 索引文件只做路由，不要求检索元数据
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        md = meta.get("metadata", {}) if isinstance(meta.get("metadata"), dict) else {}
        if not md.get("triggers"):
            problems.append(f"缺元数据：{entry['path']} 缺 metadata.triggers")
        if not md.get("summary") and not meta.get("description"):
            problems.append(f"缺元数据：{entry['path']} 缺 metadata.summary 与 description")

    scan_roots = [AGENTS_DIR / "skills", AGENTS_DIR / "knowledge", AGENTS_DIR / "memory",
                  AGENTS_DIR / "incidents", ROOT / "AGENTS.md", ROOT / "ARCHITECTURE.md"]
    scanned: set[str] = set()
    for scan_root in scan_roots:
        files = ([scan_root] if scan_root.is_file()
                 else sorted(scan_root.rglob("*.md"))) if scan_root.exists() else []
        for md_path in files:
            rel = md_path.relative_to(ROOT).as_posix()
            if rel in scanned:
                continue
            scanned.add(rel)
            text = md_path.read_text(encoding="utf-8")
            text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # 代码块内是示例树与命令，不作指针
            text = "\n".join(
                line for line in text.splitlines() if not line.lstrip().startswith("|")
            )  # 表格单元格是命名示例（见 naming.md），不当作指针
            tokens = re.findall(r"`([\w./-]+\.(?:md|py|json|toml|yml|yaml|lua|qmd))`", text)
            tokens += re.findall(r"\]\(([^)#\s]+)\)", text)
            for token in tokens:
                resolved = _resolve_pointer(token, md_path)
                if resolved is None or resolved.is_file():
                    continue
                rel_target = resolved.relative_to(ROOT).as_posix() \
                    if ROOT in resolved.parents else token
                problems.append(f"死指针：{rel} 指向不存在的 {rel_target}")

    quick_ref = QUICK_REF_PATH.relative_to(ROOT).as_posix()
    for md_path in sorted(AGENTS_DIR.rglob("*.md")):
        rel = md_path.relative_to(ROOT).as_posix()
        if rel in registered or rel == quick_ref:
            continue
        if md_path.name == "index.md":
            continue  # 领域路由页，由 MEMORY.md / KNOWLEDGE.md 承载入口
        if md_path.resolve().parent == (AGENTS_DIR / "plan").resolve():
            continue  # 计划/审计类会话文档由 ARCHITECTURE 等入口指针引用，不挂注册表
        if (AGENTS_DIR / "incidents") in md_path.resolve().parents:
            continue  # 事故案例平时不可见，由 incidents/INDEX.md 自行索引，不进 registry 与速查表
        if md_path.resolve().parent in skill_dirs or any(
            skill_dir in md_path.resolve().parents for skill_dir in skill_dirs
        ):
            continue  # 技能内 references/scripts 已随技能条目挂载
        problems.append(f"孤儿文件：{rel} 未挂载到注册表")

    incidents_dir = AGENTS_DIR / "incidents"
    if (incidents_dir / "INDEX.md").is_file():
        index_text = (incidents_dir / "INDEX.md").read_text(encoding="utf-8")
        linked: set[Path] = set()
        for token in re.findall(r"\]\(([^)#\s]+\.md)\)", index_text):
            target = (incidents_dir / token).resolve()
            if target.is_file():
                linked.add(target)
            else:
                problems.append(f"事故索引：INDEX.md 指向不存在的 {token}")
        for case_path in sorted(incidents_dir.rglob("*.md")):
            if case_path.name == "INDEX.md":
                continue
            if case_path.resolve() not in linked:
                problems.append(
                    f"事故索引：{case_path.relative_to(ROOT).as_posix()} 未登记到 INDEX.md"
                )

    if BUDGET_CHECK.is_file():
        result = subprocess.run(
            [sys.executable, str(BUDGET_CHECK)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=str(ROOT),
        )
        if result.returncode != 0:
            for line in ((result.stdout or "") + (result.stderr or "")).strip().splitlines():
                if line.strip():
                    problems.append(f"预算：{line.strip()}")
        else:
            print(f"预算：{BUDGET_CHECK.relative_to(ROOT).as_posix()} 通过")

    for line in problems:
        print(line)
    if problems:
        print(f"audit 发现 {len(problems)} 个问题")
        return 1
    print(f"audit 通过：{len(entries)} 条目，无死指针、孤儿或缺元数据")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="agent 工作区注册表工具")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="生成 registry.json 与 QUICK-REFERENCE.md")
    sub.add_parser("check", help="断言生成物与磁盘零漂移")
    search_parser = sub.add_parser("search", help="按关键词粗筛注册表")
    search_parser.add_argument("keywords", nargs="+", help="一个或多个关键词（全部命中）")
    lookup_parser = sub.add_parser("lookup", help="反向引用与全文搜索")
    lookup_parser.add_argument("keyword", help="路径片段（反向引用）或正文关键词（全文）")
    lookup_parser.add_argument("--backref", action="store_true", help="只查反向引用")
    lookup_parser.add_argument("--fulltext", action="store_true", help="只查全文搜索")
    sub.add_parser("audit", help="死指针、孤儿文件、缺元数据与篇幅预算审计")
    args = parser.parse_args(argv)
    handlers = {
        "build": cmd_build, "check": cmd_check,
        "search": cmd_search, "lookup": cmd_lookup, "audit": cmd_audit,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
