---
name: publish-governance
description: GitHub 公开仓库发布面的稳定事实与外部文档依据：生成物边界、静态校验、敏感信息处理和入口分层。
metadata:
  short-description: GitHub 发布面治理事实
  summary: 公开内容的来源、生成物、隐私与静态校验边界
  triggers:
    - GitHub
    - 发布面
    - 隐私扫描
    - 生成物
    - 静态链接
    - 唯一事实源
---

# GitHub 发布面治理

本文只记录稳定事实与公开实践，不替代 `verifying` 的执行流程。

## 发布面分层

- `README.md` 是对外展示的 Quarto 生成物，源文件是 `index.qmd` 与 `content/`。
- emoji 的边界跟随展示链路：`README.md` 生成物与它的展示内容源（`index.qmd`、`content/` 的 `.qmd`/`.md`、`_templates/`）可以携带展示 emoji；入口文档、`.agents/`、脚本、配置和 CI 文本一律不新增 emoji。静态检查按这个边界豁免，不得把 README 内容源判为违规。
- `.agents/registry.json` 与 `.agents/QUICK-REFERENCE.md` 是注册表生成物，正文来源是现存条目的 frontmatter 与入口元数据。
- `assets/banner/`、`output` 分支 SVG 和 CI 产物必须有可追溯的生成来源。
- `.gitignore`、工作流和治理文档属于受控配置，不能因为“只是工具文件”而跳过审查。

## 静态校验边界

- 必须检查生成物漂移、README 结构、注册表漂移、缓存/临时产物、路径存在性和 URL 格式。
- 外链检查只判断格式、允许域名、仓库路径和明显占位符，不依赖网络可用性。
- 敏感扫描默认阻断私钥、密钥模式、`.env` 内容、个人绝对路径和未公开联系方式；示例变量名与公开固定路径只能用精确白名单豁免。
- 动态资源的线上可访问性属于运行时诊断，不由静态校验代替。

## 外部实践

- GitHub 将 README、贡献指南、行为准则、安全说明和 CODEOWNERS 按职责分开：<https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file>
- GitHub CODEOWNERS 用路径表达评审责任：<https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners>
- OpenAI Codex 的 `AGENTS.md` 展示了全局规则与局部范围结合的做法：<https://github.com/openai/codex/blob/main/AGENTS.md>
- Microsoft Writing Style Guide 强调清晰、统一和避免重复：<https://learn.microsoft.com/en-us/style-guide/welcome/>
