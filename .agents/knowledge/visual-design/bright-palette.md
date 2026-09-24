---
name: bright-palette
description: 明亮花丛色板 token 与 Shields 参数示例：浅色/深色主题色值，取自横幅画面。
metadata:
  short-description: 明亮花丛色板 token
  summary: 浅色/深色主题色板 token 与 Shields 参数示例
  triggers:
    - 色板
    - 色值
    - token
    - 配色
    - shields
---

# 明亮花丛色板

配色取自横幅画面 `assets/banner/pixel-flower-landscape-64color.png`：像素风花朵山水，白天溪谷花丛，光线偏暖。整体明亮、低饱和，避免深色底与霓虹色。

## Token

| 用途 | 色值 | 说明 |
|------|------|------|
| 页面主背景 | `#FFFFFF` | 徽章正文底 |
| 浅米底 | `#F3EFE6` | 徽章 label 底、分区底色 |
| 主文字 | `#2F3E2E` | 深苔绿，替代纯黑 |
| 次文字 | `#4A5560` | 暖褐灰，用于说明文字 |
| 叶绿 | `#E6F1E4` / `#3F7D3A` | 底 / 前景，对应 Python、GitHub 链接徽章 |
| 溪流蓝 | `#E4EFF7` / `#3E6FA8` | 底 / 前景，对应 C++ |
| 花品红 | `#F7E9EF` / `#C46A85` | 底 / 前景，对应 GitHub Actions、站点链接 |
| 暖黄 | `#FBF3DF` / `#B08A3E` | 底 / 前景，对应 Quarto |

## Shields 用法

- 技能类徽章：`style=for-the-badge`，`color` 用浅底，`logoColor` 用深前景。
- 链接类徽章：`style=flat-square`，`labelColor=F3EFE6`，`color=FFFFFF`。
- 推荐项目不使用指标徽章（最近更新、协议等），判断见 `designing-visuals` 的「推荐项目列表样式」。

示例：

```text
https://img.shields.io/badge/Python-E6F1E4?style=for-the-badge&logo=python&logoColor=3F7D3A
```

## 统计卡 SVG 用色

`.agents/skills/designing-visuals/scripts/stats/gen_stats.py` 为账号统计与常用语言各生成浅色、深色两张卡片，README 用 `<picture>` 按 `prefers-color-scheme` 切换。

### 浅色（白昼溪谷）

直接取上表 token：

| 元素 | 色值 |
|------|------|
| 卡片底 | `#F3EFE6` |
| 页面底 | `#FFFFFF` |
| 主文字与数值 | `#2F3E2E` |
| 次文字与占比 | `#4A5560` |
| 条形与色块强调 | `#3F7D3A`、`#3E6FA8`、`#C46A85`、`#B08A3E`、`#4A5560` 依次循环 |
| 卡片描边 | `#4A5560`，`stroke-opacity="0.12"`，用于分区轮廓，不新增色值 |

### 深色（蓝调时刻）

沿用 GitHub 深色画布体系，强调色对应加亮，保持深色下的对比度：

| 元素 | 色值 |
|------|------|
| 卡片底 | `#161B22`，与贪吃蛇深色画布同一体系 |
| 主文字与数值 | `#F0F6FC` |
| 次文字与占比 | `#C9D1D9` |
| 条形与色块强调 | `#56D364`、`#58A6FF`、`#DB61A2`、`#D29922`、`#C9D1D9` 依次循环 |
| 卡片描边 | `#C9D1D9`，`stroke-opacity="0.12"` |

Shields 徽章不区分深浅主题：徽章本体是浅色 chip，放在深色画布上仍可读，与现有技术栈徽章保持一致。

## 贪吃蛇标注用色

`.agents/skills/designing-visuals/scripts/activity/add_labels.py` 叠加的月份/星期标注文字色：

| 主题 | 文字 |
|------|------|
| 浅色 | `#4A5560` |
| 深色 | `#8B949E` |

浅色与统计卡次文字同一体系；深色沿用 GitHub 深色主题的次级文字，保证两种画布可读。

## 约束

- 不使用深色底徽章，One Dark 一类的深色配色与明亮横幅冲突。
- 不使用霓虹色、发光描边和彩虹渐变；强调色饱和度保持克制。
- 同一页面只使用上表色值，不临时新增颜色。
- HTML 属性里的 `&` 写成 `&amp;`。

页面层面的明亮风格判断（层次、布局、节奏）见 `designing-visuals` 技能的「明亮风格」一节。视觉方向锚定新海诚式电影感：柔光、天空与水面分层、低饱和暖色，浅色底保证长文可读；深色对应「蓝调时刻」——深蓝灰画布、近白文字、加亮但克制的强调色。这套界面的设计术语是「电影感编辑式极简」（cinematic minimalism / editorial minimalism）：色值收敛为 token，数据以高信息密度极简界面（data-dense minimal UI）呈现；「新海诚式」是视觉来源，不是可执行的官方规范。