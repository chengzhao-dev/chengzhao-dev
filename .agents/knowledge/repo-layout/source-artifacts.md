---
name: source-artifacts
description: 仓库源文件、生成物与工具解析顺序的事实清单：目录职责、Quarto 配置逐项说明、FFmpeg/FFprobe 解析优先级。
metadata:
  short-description: 源文件与产物事实
  summary: 仓库目录职责、Quarto 配置事实与 FFmpeg/FFprobe 五级解析顺序
  triggers:
    - 源文件
    - 产物
    - toolchain
    - ffmpeg
    - config.toml
    - _quarto.yml
    - 目录职责
---

# 源文件、产物与本机工具

渲染、预览与发布流程见技能 `maintaining-readme`；本文件只记事实与参数。

## 源文件与产物

- `index.qmd` 是唯一手工编辑的工程文件，负责页面顺序与组件布局；`content/` 按页面顺序拆成 `header.md`、`tech-stack.md`、`repositories.md`、`activity.md`、`stats.md`、`contact.md`，由 `index.qmd` 依次 include。
- `_templates/readme.markdown` 是去掉前导空行的最小模板；`assets/banner/` 保存 README 直接引用的横幅媒体，`assets/source/` 保存横幅原始素材。
- 可执行自动化放在 `.agents/skills/*/scripts/`（人与 CI 共用）：`designing-visuals/scripts/media/` 媒体工具链、`designing-visuals/scripts/stats/` 统计卡、`designing-visuals/scripts/activity/` 贡献图标注、`verifying/scripts/verify/` 结构与规范断言、`maintaining-readme/scripts/filters/` Quarto Lua 过滤器、`governing-agents/scripts/` 注册表与检索。
- `.agents/skills/designing-visuals/scripts/media/toolchain.py` 是共用的工具解析；`.agents/skills/designing-visuals/scripts/media/bootstrap_media.py` 按固定版本/URL/SHA-256 下载 FFmpeg 与 FFprobe；`.agents/skills/designing-visuals/scripts/media/gen_banner.py` 生成两份横幅资源，改参数要改脚本后重新生成，不手改生成物。
- 根目录 `config.toml` 是唯一的项目配置：记录 Python 解释器、FFmpeg/FFprobe 路径与工具缓存目录，默认留空即走 PATH；换机器只改这一个文件。
- `_quarto.yml` 只声明 `gfm` 格式、`output-file: README.md`，用 `default-image-extension: ""` 关闭给远程图片地址追加扩展名，并用 `template: _templates/readme.markdown` 启用最小模板。
- `.agents/skills/maintaining-readme/scripts/filters/github-align.lua` 把 Quarto 的 `data-align` 还原为 GitHub 认得的 `align`，是当前唯一保留的过滤器；`repo-table.lua` 已随推荐项目列表化（2026-09）移除。
- `index.qmd` 不设 `title`，避免 README 顶部多出与问候语重复的一级标题。
- 仓库只输出 `README.md`，不生成也不提交 HTML 产物。

## 本机工具解析顺序

`.agents/skills/designing-visuals/scripts/media/toolchain.py` 按优先级从高到低解析 FFmpeg/FFprobe：

1. 命令行显式传入（`--ffmpeg` / `--ffprobe`）
2. 环境变量 `FFMPEG` / `FFPROBE`
3. 根目录 `config.toml`
4. `.agents/skills/designing-visuals/scripts/media/tool-cache/ffmpeg/<版本>/bin/`
5. 系统 PATH

FFmpeg 二进制不进入版本库，`tool-cache/` 已被忽略；本机解释器现状见 `local-env/python.md`。
