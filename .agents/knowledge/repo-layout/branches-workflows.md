---
name: branches-workflows
description: 分支职责与 Actions 产物的事实清单：output 分支资源、SVG 清单与生成顺序、readme.yml/snake.yml 分工、忽略规则。
metadata:
  short-description: 分支与工作流事实
  summary: output 分支六个 SVG、工作流分工与 .gitignore 必须保持的忽略清单
  triggers:
    - output 分支
    - snake.yml
    - readme.yml
    - svg
    - gitignore
    - 工作流
    - 生成顺序
---

# 分支与工作流事实

发布与提交的流程规范见技能 `maintaining-readme` 的 `references/repo-and-release.md`；本文件只记事实。

## 分支职责

- `main` 是 Profile README 的唯一发布源与默认分支；GitHub 只读取默认分支根目录的 `README.md`。
- `output` 分支只存放 `snake.yml` 生成的动态资源，由 README 经 `raw.githubusercontent.com` 外链引用，不承载页面内容；删除它会直接导致贡献图与统计卡失效。

## output 分支资源

六个 SVG：浅色/深色贪吃蛇各一张，账号统计与常用语言统计卡浅色/深色各一张。

- `.agents/skills/designing-visuals/scripts/stats/gen_stats.py` 用 GitHub API 生成四张统计卡，只用标准库；与贡献图共用同一次 `output` 发布步骤。
- `.agents/skills/designing-visuals/scripts/activity/add_labels.py` 为贪吃蛇 SVG 叠加 GitHub 风格的月份与星期标注，统计窗口由运行当天向前推 364 天。

## 工作流分工

- `.github/workflows/readme.yml`：重新渲染并校验 `README.md` 与源文件一致。
- `.github/workflows/snake.yml`：按公开贡献记录刷新 `output` 分支；生成顺序固定为贡献图 SVG → 月份/星期标注 → 统计卡 → 发布。
- 两个工作流保持最小权限；不部署 GitHub Pages，不提交 HTML 产物或 Quarto 缓存。

## 忽略规则

- `.gitignore` 按系统文件、编辑器、ZCode 本地产物、Quarto、构建缓存、语言缓存、密钥、日志与本机工具分组，使用中文注释；Agent 暂存目录 `temp/` 保持忽略。
- 不要忽略受控源文件：`content/`、`assets/`、`config.toml`、`_templates/`、`.agents/`、`.github/` 与生成的 `README.md`；`.agents/skills/designing-visuals/scripts/media/tool-cache/` 必须保持忽略。
- `.zcodeignore` 与 `.zcode/` 是本机配置，只保留在本地，既不提交也不删除。
