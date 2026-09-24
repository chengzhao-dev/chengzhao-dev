#!/usr/bin/env python3
"""为贪吃蛇贡献图 SVG 添加 GitHub 风格的月份与星期标注。

snk 生成的 SVG 只有贡献格子，没有坐标文字。本脚本读取浅色/深色两个版本的
SVG，从格子 rect 解析贡献网格的行列坐标，在网格上方标注英文月份缩写、
左侧标注 Mon/Wed/Fri，样式与 GitHub 个人主页的贡献图一致；统计窗口随
--end（默认今天）动态计算，图内不写死具体日期。只使用标准库，CI 无需装依赖。

用法：
  python3 .agents/skills/designing-visuals/scripts/activity/add_labels.py \
    --light dist/github-contribution-grid-snake.svg \
    --dark dist/github-contribution-grid-snake-dark.svg
"""

from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

LABEL_CLASS = "activity-labels"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',Helvetica,Arial,sans-serif"

# 标注参数对齐 GitHub 贡献图：字号 10，星期缩写右端距网格 7，月份缩写
# 基线在网格上方 7；左侧/顶部预留容纳文字的边距，不够时扩画布。
FONT_SIZE = 10
WEEKDAY_GAP = 7
MONTH_LIFT = 7
GUTTER_LEFT = 30
GUTTER_TOP = 16

# 标注文字颜色：浅色与统计卡的次级文字一致，深色沿用 GitHub 深色主题
# 的次级文字，保证两种画布上都可读。
THEMES = {"light": "#4A5560", "dark": "#8B949E"}

MONTH_ABBRS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
# 贡献图行序从周日开始，GitHub 在周一/周三/周五三行显示星期缩写。
WEEKDAY_LABELS = ((1, "Mon"), (3, "Wed"), (5, "Fri"))

# 旧版脚本追加的底部日期条：重跑时识别并一并移除。
LEGACY_BAND_HEIGHT = 40

SVG_RE = re.compile(r"<svg\b[^>]*\bviewBox=\"([^\"]+)\"[^>]*>")
RECT_RE = re.compile(r"<rect\b[^>]*>")
CELL_CLASS_RE = re.compile(r'class="c(?:\s[^"]*)?"')
LABEL_GROUP_RE = re.compile(r'<g class="activity-labels"[^>]*>.*?</g>', re.S)
LEGACY_BAND_RE = re.compile(r'<g class="activity-date"[^>]*>.*?</g>', re.S)


def parse_viewbox(svg: str) -> tuple[float, float, float, float] | None:
    match = SVG_RE.search(svg)
    if not match:
        return None
    parts = match.group(1).split()
    if len(parts) != 4:
        return None
    try:
        return tuple(float(p) for p in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def set_viewbox(svg: str, x: float, y: float, width: float, height: float) -> str:
    # svg 标签是文档第一个元素，count=1 只会命中它的属性；CSS 里的
    # width:/height: 是冒号写法，不会被误改。
    svg = re.sub(r'viewBox="[^"]*"', f'viewBox="{x:g} {y:g} {width:g} {height:g}"', svg, count=1)
    svg = re.sub(r'\bwidth="[^"]*"', f'width="{width:g}"', svg, count=1)
    svg = re.sub(r'\bheight="[^"]*"', f'height="{height:g}"', svg, count=1)
    return svg


def attr_value(tag: str, name: str) -> float | None:
    match = re.search(rf'\b{name}="(-?[\d.]+)"', tag)
    return float(match.group(1)) if match else None


def parse_grid(svg: str) -> tuple[list[float], list[float], float]:
    """从格子 rect 解析出各列 x、各行 y 与格子边长。"""
    cells = [t for t in RECT_RE.findall(svg) if CELL_CLASS_RE.search(t)]
    xs = sorted({v for t in cells if (v := attr_value(t, "x")) is not None})
    ys = sorted({v for t in cells if (v := attr_value(t, "y")) is not None})
    if len(xs) < 40 or len(ys) != 7:
        raise ValueError(f"无法识别贡献网格（解析到 {len(xs)} 列 × {len(ys)} 行）")
    # lookbehind 排除 stroke-width，只认独立的 width: 声明
    css = re.search(r"\.c\{[^}]*?(?<![-\w])width:([\d.]+)px", svg)
    cell = float(css.group(1)) if css else ys[1] - ys[0] - 4
    return xs, ys, cell


def month_labels(xs: list[float], grid_start: date) -> list[tuple[int, str]]:
    """GitHub 规则：月份在周日列上变化的那一列标注月份缩写，
    与上一标签相距不足两列时省略，避免文字重叠。"""
    labels: list[tuple[int, str]] = []
    prev_month = 0
    last_col = -2
    for col in range(len(xs)):
        day = grid_start + timedelta(days=7 * col)
        if day.month != prev_month and col - last_col >= 2:
            labels.append((col, MONTH_ABBRS[day.month - 1]))
            last_col = col
        prev_month = day.month
    return labels


def reset_svg(svg: str) -> str:
    """移除已生成的标注组并还原 snk 原始画布，保证重复运行结果稳定。"""
    recorded = re.search(r'<g class="activity-labels"[^>]*data-viewbox="([^"]*)"', svg)
    had_legacy_band = '<g class="activity-date"' in svg
    svg = LABEL_GROUP_RE.sub("", svg)
    svg = LEGACY_BAND_RE.sub("", svg)
    if recorded:
        parts = recorded.group(1).split()
        if len(parts) == 4:
            return set_viewbox(svg, *(float(p) for p in parts))
    if had_legacy_band:
        # 旧版日期条曾在底部追加 40 高度，去掉后一并还原。
        viewbox = parse_viewbox(svg)
        if viewbox is None:
            raise ValueError("无法解析 SVG 的 viewBox")
        x, y, width, height = viewbox
        svg = set_viewbox(svg, x, y, width, height - LEGACY_BAND_HEIGHT)
    return svg


def embed_labels(svg: str, theme: str, grid_start: date) -> str:
    xs, ys, cell = parse_grid(svg)
    original = parse_viewbox(svg)
    if original is None:
        raise ValueError("无法解析 SVG 的 viewBox")
    ox, oy, ow, oh = original
    x0, y0, width, height = ox, oy, ow, oh

    if xs[0] - x0 < GUTTER_LEFT:  # 左侧留出星期缩写的位置
        shift = GUTTER_LEFT - (xs[0] - x0)
        x0 -= shift
        width += shift
    if ys[0] - y0 < GUTTER_TOP:  # 顶部留出月份缩写的位置
        shift = GUTTER_TOP - (ys[0] - y0)
        y0 -= shift
        height += shift

    fg = THEMES[theme]
    texts = [
        f'<text x="{xs[col]:g}" y="{ys[0] - MONTH_LIFT:g}" '
        f'font-family="{FONT}" font-size="{FONT_SIZE}" fill="{fg}">{label}</text>'
        for col, label in month_labels(xs, grid_start)
    ]
    texts += [
        f'<text x="{xs[0] - WEEKDAY_GAP:g}" y="{ys[row] + cell / 2 + FONT_SIZE * 0.35:g}" '
        f'text-anchor="end" font-family="{FONT}" font-size="{FONT_SIZE}" fill="{fg}">{label}</text>'
        for row, label in WEEKDAY_LABELS
    ]
    group = (
        f'<g class="{LABEL_CLASS}" data-viewbox="{ox:g} {oy:g} {ow:g} {oh:g}">'
        + "".join(texts)
        + "</g>"
    )
    svg = set_viewbox(svg, x0, y0, width, height)
    return svg.replace("</svg>", group + "</svg>")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="为贪吃蛇贡献图 SVG 添加 GitHub 风格月份/星期标注")
    parser.add_argument("--light", required=True, help="浅色版 SVG 路径")
    parser.add_argument("--dark", required=True, help="深色版 SVG 路径")
    parser.add_argument(
        "--end",
        default=None,
        help="统计窗口结束日期 YYYY-MM-DD，默认今天",
    )
    args = parser.parse_args(argv)

    end = date.fromisoformat(args.end) if args.end else date.today()
    start = end - timedelta(days=364)  # GitHub 贡献图显示最近一年（含结束日）
    grid_start = start - timedelta(days=(start.weekday() + 1) % 7)  # 回退到所在周的周日

    for path, theme in ((args.light, "light"), (args.dark, "dark")):
        file_path = Path(path)
        if not file_path.is_file():
            raise SystemExit(f"缺少 SVG 文件：{file_path}")
        svg = reset_svg(file_path.read_text(encoding="utf-8"))
        updated = embed_labels(svg, theme, grid_start)
        # 断言标注组已写入、旧版日期条未回流，防止用不完整的输出覆盖原文件。
        if '<g class="activity-labels"' not in updated or "activity-date" in updated:
            raise SystemExit(f"{file_path} 的标注组缺失或仍残留旧版日期条，放弃写入")
        file_path.write_text(updated, encoding="utf-8")
        print(f"已写入 {file_path}：{grid_start.isoformat()} 至 {end.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
