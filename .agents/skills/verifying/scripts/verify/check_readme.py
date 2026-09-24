#!/usr/bin/env python3
"""校验生成的 README.md 是否满足结构规范，本地与 CI 共用同一套断言。

用法：
  python .agents/skills/verifying/scripts/verify/check_readme.py

只使用标准库。输出一行一条结论，全部通过时打印 PASS 汇总并以 0 退出。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
README = ROOT / "README.md"

ALLOWED_REMOTE_PREFIXES = (
    "https://raw.githubusercontent.com/chengzhao-dev/chengzhao-dev/output/",
    "https://img.shields.io/",
)

# 章节标题的图标 emoji 属于 README 生成内容；这里用 Unicode 码位书写，保持源文本无 emoji 字面量。
SECTION_TECH = "## \U0001F6E0\uFE0F 技术栈"
SECTION_REPOS = "## \U0001F4E6 推荐仓库"
SECTION_ACTIVITY = "## \U0001F4C8 过去一年贡献"
SECTION_STATS = "## \u2699\uFE0F GitHub 统计"
SECTION_CONTACT = "## \U0001F517 与我相关"

SECTIONS = (SECTION_TECH, SECTION_REPOS, SECTION_ACTIVITY, SECTION_STATS, SECTION_CONTACT)


def section(text: str, title: str) -> str:
    """取某个二级标题到下一个二级标题之间的正文；章节缺失时返回空串。"""
    if title not in text:
        return ""
    start = text.index(title)
    next_titles = [text.index(t) for t in SECTIONS if t != title and text.index(t) > start]
    return text[start : min(next_titles) if next_titles else len(text)]


def main() -> int:
    findings: list[str] = []

    def check(ok: bool, name: str, detail: str = "") -> bool:
        if not ok:
            findings.append(f"{name}{('：' + detail) if detail else ''}")
        return ok

    try:
        text = README.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        findings.append(f"UTF-8：解码失败（{exc}）")
        report(findings)
        return 1

    lines = text.splitlines()
    check(lines and lines[0].startswith('<div align="center">'), "首行是横幅 div，顶部无前导空行")
    banner_end = text.find("</div>")
    if banner_end != -1:
        banner = text[:banner_end]
        check('<source srcset=' in banner and 'type="image/webp"' in banner, "横幅含 WebP source")
        check("<img" in banner and "alt=" in banner, "横幅降级 img 带 alt")
    else:
        check(False, "未找到横幅 </div>")

    for title in SECTIONS:
        check(title in text, f"章节存在：{title}")

    check("<table" not in text and "repo-table" not in text, "无表格与 repo-table 容器")
    check("last-commit" not in text and "img.shields.io/github/license" not in text, "无最近更新/协议指标徽章")
    check("data-align" not in text, "无 data-align 残留")

    repos = section(text, SECTION_REPOS)
    list_start = repos.find("- [")
    intro = repos[:list_start] if list_start != -1 else ""
    check("全部公开仓库" in intro and "ARCHITECTURE.md" in intro, "推荐仓库说明含全部公开仓库与 ARCHITECTURE.md 指针")
    tail = [ln for ln in repos[list_start:].splitlines() if ln.strip()]
    check(bool(tail) and tail[-1].startswith("- "), "推荐仓库列表下方无补充句")

    activity = section(text, SECTION_ACTIVITY)
    check(
        activity.find("图片由本仓库的 Actions") != -1
        and activity.find("图片由本仓库的 Actions") < activity.find("<picture>"),
        "贡献图说明在图片上方",
    )
    check("过去一年：" not in text and not re.search(r"一年：20\d\d", text), "正文无独立日期标注")

    for num, img in enumerate(re.findall(r"<img\b[^>]*>", text), 1):
        check("alt=" in img, f"第 {num} 个 img 带 alt")

    for num, url in enumerate(re.findall(r'src="([^"]+)"', text), 1):
        check(url.startswith(ALLOWED_REMOTE_PREFIXES) or not url.startswith("http"), f"第 {num} 个远程来源在白名单内", url)
    check("https://github.com/chengzhao-dev" in section(text, SECTION_STATS), "统计卡含主页降级链接")

    report(findings)
    return 1 if findings else 0


def report(findings: list[str]) -> None:
    for item in findings:
        print(f"FAIL: {item}")
    print(f"{'PASS' if not findings else 'FAIL'}: {len(findings)} 处问题")


if __name__ == "__main__":
    raise SystemExit(main())
