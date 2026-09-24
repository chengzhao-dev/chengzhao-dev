#!/usr/bin/env python3
"""根据 GitHub 公开数据生成浅色与深色两套静态 SVG 统计卡。

输出浅色/深色各两张：`github-stats.svg` / `github-stats-dark.svg`（账号统计）
与 `github-languages.svg` / `github-languages-dark.svg`（常用语言），
由 `.github/workflows/snake.yml` 推送到 `output` 分支，供 README 通过
`raw.githubusercontent.com` 引用。配色取自 `.agents/knowledge/visual-design/bright-palette.md`，
不依赖第三方统计服务。

只使用标准库，CI 里无需安装依赖。
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

API_ROOT = "https://api.github.com"
GRAPHQL_ROOT = "https://api.github.com/graphql"

# 主题 token 见 .agents/knowledge/visual-design/bright-palette.md：浅色是明亮花丛
# 色板，深色是配套的 GitHub 深色画布版本，强调色加亮以保持深色下的对比度。
THEMES = {
    "light": {
        "panel_bg": "#F3EFE6",
        "text_main": "#2F3E2E",
        "text_sub": "#4A5560",
        "accents": ("#3F7D3A", "#3E6FA8", "#C46A85", "#B08A3E", "#4A5560"),
    },
    "dark": {
        "panel_bg": "#161B22",
        "text_main": "#F0F6FC",
        "text_sub": "#C9D1D9",
        "accents": ("#56D364", "#58A6FF", "#DB61A2", "#D29922", "#C9D1D9"),
    },
}

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',Helvetica,Arial,sans-serif"

STATS_WIDTH = 900
STATS_HEIGHT = 300
LANGUAGES_WIDTH = 900
LANGUAGES_HEIGHT = 340
TOP_LANGUAGES = 5


def xml_escape(value: object) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def request_json(url: str, token: str, *, payload: dict | None = None, attempts: int = 3) -> dict:
    """请求 GitHub API，失败时短暂重试。"""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "chengzhao-dev-profile-stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"请求 {url} 失败：{last_error}")


def gather_stats(owner: str, token: str) -> dict[str, int]:
    """取账号层面的公开指标，包含过去一年的贡献数。"""
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false) { totalCount }
        followers { totalCount }
        contributionsCollection {
          contributionCalendar { totalContributions }
          totalCommitContributions
        }
      }
    }
    """
    data = request_json(GRAPHQL_ROOT, token, payload={"query": query, "variables": {"login": owner}})
    if "errors" in data:
        raise RuntimeError(f"GraphQL 返回错误：{data['errors']}")
    user = data["data"]["user"]
    collection = user["contributionsCollection"]
    return {
        "公开仓库": user["repositories"]["totalCount"],
        "关注者": user["followers"]["totalCount"],
        "过去一年提交": collection["totalCommitContributions"],
        "过去一年贡献": collection["contributionCalendar"]["totalContributions"],
    }


def gather_languages(owner: str, token: str) -> list[tuple[str, int]]:
    """汇总公开、非 fork 仓库的语言字节数，返回占比最高的若干项。"""
    repos = request_json(
        f"{API_ROOT}/users/{owner}/repos?per_page=100&type=owner&sort=pushed",
        token,
    )
    totals: dict[str, int] = {}
    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        if not repo.get("language"):
            continue
        languages = request_json(repo["languages_url"], token)
        for name, size in languages.items():
            totals[name] = totals.get(name, 0) + int(size)

    if not totals:
        return []

    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:TOP_LANGUAGES]
    total = sum(totals.values())
    return [(name, round(size * 100 / total)) for name, size in ranked]


def render_stats_svg(stats: dict[str, int], theme_name: str) -> str:
    theme = THEMES[theme_name]
    panel_bg = theme["panel_bg"]
    text_main = theme["text_main"]
    text_sub = theme["text_sub"]
    accents = theme["accents"]
    columns = 2
    tile_width = 414
    tile_height = 88
    gap = 24
    start_x = 24
    start_y = 76

    tiles = []
    for index, (label, value) in enumerate(stats.items()):
        col = index % columns
        row = index // columns
        x = start_x + col * (tile_width + gap)
        y = start_y + row * (tile_height + gap)
        accent = accents[index % len(accents)]
        tiles.append(
            f'<rect x="{x}" y="{y}" width="{tile_width}" height="{tile_height}" rx="12" fill="{panel_bg}" '
            f'stroke="{text_sub}" stroke-opacity="0.12"/>'
            f'<rect x="{x}" y="{y}" width="4" height="{tile_height}" rx="2" fill="{accent}"/>'
            f'<text x="{x + 24}" y="{y + 34}" font-family="{FONT}" font-size="15" fill="{text_sub}">{xml_escape(label)}</text>'
            f'<text x="{x + 24}" y="{y + 68}" font-family="{FONT}" font-size="28" font-weight="700" fill="{text_main}">{xml_escape(value)}</text>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{STATS_WIDTH}" height="{STATS_HEIGHT}" '
        f'viewBox="0 0 {STATS_WIDTH} {STATS_HEIGHT}" role="img" aria-label="GitHub 账号统计">\n'
        f'  <text x="24" y="44" font-family="{FONT}" font-size="20" font-weight="700" fill="{text_main}">账号统计</text>\n'
        f"  {'  '.join(tiles)}\n"
        f"</svg>\n"
    )


def render_languages_svg(languages: list[tuple[str, int]], theme_name: str) -> str:
    theme = THEMES[theme_name]
    panel_bg = theme["panel_bg"]
    text_main = theme["text_main"]
    text_sub = theme["text_sub"]
    accents = theme["accents"]
    # 页边距与账号统计卡对齐（24），两张卡并排阅读时左缘一致。
    bar_x = 24
    bar_width = LANGUAGES_WIDTH - bar_x * 2
    row_height = 52
    start_y = 84

    rows = []
    for index, (name, percent) in enumerate(languages):
        y = start_y + index * row_height
        accent = accents[index % len(accents)]
        filled = max(round(bar_width * percent / 100), 6)
        rows.append(
            f'<text x="{bar_x}" y="{y}" font-family="{FONT}" font-size="17" fill="{text_main}">{xml_escape(name)}</text>'
            f'<text x="{bar_x + bar_width}" y="{y}" text-anchor="end" font-family="{FONT}" font-size="16" fill="{text_sub}">{percent}%</text>'
            f'<rect x="{bar_x}" y="{y + 10}" width="{bar_width}" height="10" rx="5" fill="{panel_bg}"/>'
            f'<rect x="{bar_x}" y="{y + 10}" width="{filled}" height="10" rx="5" fill="{accent}"/>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LANGUAGES_WIDTH}" height="{LANGUAGES_HEIGHT}" '
        f'viewBox="0 0 {LANGUAGES_WIDTH} {LANGUAGES_HEIGHT}" role="img" aria-label="GitHub 常用语言占比">\n'
        f'  <text x="24" y="44" font-family="{FONT}" font-size="20" font-weight="700" fill="{text_main}">常用语言</text>\n'
        f"  {'  '.join(rows)}\n"
        f"</svg>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 GitHub 统计静态 SVG")
    parser.add_argument("--owner", required=True, help="GitHub 用户名")
    parser.add_argument("--output-dir", default="dist", help="SVG 输出目录")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""), help="GitHub token，默认读 GITHUB_TOKEN")
    args = parser.parse_args(argv)

    if not args.token:
        raise SystemExit("缺少 GitHub token：请设置 GITHUB_TOKEN 或传入 --token")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stats = gather_stats(args.owner, args.token)
    languages = gather_languages(args.owner, args.token)
    if not languages:
        raise SystemExit("没有取到任何语言数据，放弃覆盖已有 SVG")

    outputs = {
        "github-stats.svg": render_stats_svg(stats, "light"),
        "github-stats-dark.svg": render_stats_svg(stats, "dark"),
        "github-languages.svg": render_languages_svg(languages, "light"),
        "github-languages-dark.svg": render_languages_svg(languages, "dark"),
    }
    for filename, content in outputs.items():
        if not (content.lstrip().startswith("<svg") and content.rstrip().endswith("</svg>")):
            raise SystemExit(f"生成的 {filename} 不是合法 SVG，放弃写入")
        (output_dir / filename).write_text(content, encoding="utf-8")
        print(f"已生成 {output_dir / filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())