# 知识库索引

本目录保存 Profile README 的参考材料：事实、色值与参数区间，是查阅用的背景资料，不是可执行流程；流程见 `.agents/skills/`，硬性约束见根目录 `AGENTS.md`。

## 视觉设计

- [明亮花丛色板](visual-design/bright-palette.md)：浅色/深色主题色板 token 与 Shields 参数示例。
- [横幅媒体参数](visual-design/banner-media.md)：横幅 WebP/静态降级的生成参数、体积上限与重新生成方式。

## 组件信任

- [组件信任层级](component-trust/trust-tiers.md)：外部组件的信任层级，允许与禁止的清单。

## 仓库布局

- [源文件与产物](repo-layout/source-artifacts.md)：目录职责、Quarto 配置事实与 FFmpeg/FFprobe 解析顺序。
- [分支与工作流](repo-layout/branches-workflows.md)：output 分支资源、工作流分工与忽略规则。
- [GitHub 发布面治理](repo-layout/publish-governance.md)：公开内容的来源、生成物、隐私与静态校验边界。

## 本机环境

- [Python 解释器](local-env/python.md)：本机 miniforge3 解释器位置与统一用法，唯一事实源在 `config.toml`。
