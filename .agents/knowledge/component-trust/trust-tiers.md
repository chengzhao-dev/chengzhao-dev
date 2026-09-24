---
name: trust-tiers
description: 外部组件的信任层级事实：允许与禁止的清单、四级判定方法。
metadata:
  short-description: 组件信任层级事实
  summary: 允许与禁止引用的外部资源清单及四级判定方法
  triggers:
    - 组件
    - 信任
    - shields
    - 统计卡
    - 第三方
    - 禁止
---

# 组件信任层级

Profile README 允许引用的外部资源，按可靠性从高到低分为四级。选择组件时从第 1 级往下找，够用就不升级到下一级。

## 1. GitHub 官方托管（首选）

资源由 GitHub 自己生成或托管，可离线校验、无第三方配额。

- 仓库内静态资源：`assets/` 下的 SVG，底图 base64 内嵌，不依赖任何外链。
- `raw.githubusercontent.com/<owner>/<repo>/<branch>/...`：本仓库 `output` 分支的贪吃蛇 SVG，以及 `.agents/skills/designing-visuals/scripts/stats/gen_stats.py` 生成的 `github-stats.svg`、`github-languages.svg` 统计卡。
- `opengraph.githubassets.com/1/<owner>/<repo>`：仓库社交预览图，GitHub 官方生成，随仓库信息自动更新。
- 数据来源一律用 GitHub REST API 或 `gh` 核实后再写进文案。

## 2. 成熟公开徽章服务

- [Shields.io](https://shields.io/)：本仓库已在用，服务规模大、被 VS Code / Vue / Bootstrap 等项目使用，支持 `github/stars`、`github/license`、`github/last-commit` 等动态徽章。
- 使用约束：同类徽章 `style` 保持一致；指标为空（如 0 star）时不展示；参数中的 `&` 在 HTML 属性里写成 `&amp;`。

## 3. 可用但需自建

需要动态统计（提交数、语言占比）时，优先用 GitHub Actions 在本仓库生成静态 SVG，再推到 `output` 分支通过 `raw.githubusercontent.com` 引用。数据与托管都在 GitHub，不依赖公共实例。

- 账号统计与常用语言卡片由 `.agents/skills/designing-visuals/scripts/stats/gen_stats.py` 生成，和贪吃蛇共用 `.github/workflows/snake.yml` 的同一次 `output` 发布，避免两个 workflow 互相覆盖。
- 自建静态 SVG 是唯一允许的统计卡形态：不直接引用社区公共 stats 域名（例如 `github-readme-stats*.vercel.app`），它们由个人或小团队维护，限流、易失效，且与官方无关。
- 官方并没有提供可嵌入的「个人 stats 卡片」API，遇到声称是官方接口的说法先核实。

## 4. 禁止引入

- 需要 JavaScript、登录或客户端执行的组件。
- 无法在仓库内自建、无法验证可用性的第三方动态服务（`coolreadme.xyz`、`readme-typing-svg.demolab.com` 之类）。
- 依赖单一来源、随时可能下线的统计卡或动态图服务。
- GIF、APNG、视频和第三方动态图服务。

## 判定方法

1. 资源能否由本仓库或 GitHub 自己生成？能则用第 1 级。
2. 只是标签和公开指标？用 Shields.io。
3. 需要聚合数据？写 GitHub Actions 生成静态 SVG。
4. 都不满足就放弃该组件，用文字或链接替代，不为了效果引入不可控依赖。