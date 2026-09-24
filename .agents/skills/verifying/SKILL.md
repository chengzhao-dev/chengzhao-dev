---
name: verifying
description: 本仓库构建与校验的唯一命令入口：Quarto 渲染、README 结构断言、横幅资源校验、agent 注册表零漂移检查与可选规范审计。改动源文件后需要构建、验证结果或排查 CI 校验失败时使用。
metadata:
  short-description: 构建与校验命令入口
  summary: Quarto 渲染与全套本地校验命令的统一入口
  triggers:
    - 构建
    - 校验
    - 渲染
    - verify
    - check
    - audit
  paths:
    - "_quarto.yml"
    - "index.qmd"
    - "content/**"
    - ".agents/skills/**/scripts/**"
    - "assets/**"
---

# 构建与校验命令

## 渲染与预览

- 根目录执行 `quarto render` 生成 `README.md`；再执行一次并确认 `git diff --quiet README.md` 成立（渲染幂等）。
- 本地预览：`quarto preview README.md --no-browser --no-watch-inputs`。
- 首次构建缺 FFmpeg/FFprobe 时执行 `python .agents/skills/designing-visuals/scripts/media/bootstrap_media.py` 下载到缓存目录。

## 校验命令

按需在仓库根目录用当前环境的 `python` 执行；输出一行一条、结论简洁：

| 命令 | 职责 |
|---|---|
| `python .agents/skills/verifying/scripts/verify/run_all.py` | 依次运行下表全部静态校验并汇总退出码（统一入口；`--skip-banner` 跳过媒体检查） |
| `python .agents/skills/verifying/scripts/verify/check_readme.py` | README 结构断言（说明位置、徽章、alt、来源白名单） |
| `python .agents/skills/verifying/scripts/verify/check_commit_attribution.py` | 提交归属检查：git 历史不得含 Cursor 共著或 Cursor 身份 |
| `python .agents/skills/verifying/scripts/verify/check_publish.py` | GitHub 发布面静态检查：敏感内容、机器路径与允许域名 |
| `python .agents/skills/verifying/scripts/verify/check_workflows.py` | 工作流权限/并发/引用与忽略规则（需 PyYAML） |
| `python .agents/skills/designing-visuals/scripts/media/gen_banner.py --check` | 横幅资源可解码，尺寸、时长与用色正确；参数唯一来源是 `.agents/skills/designing-visuals/scripts/media/banner_spec.py` |
| `python .agents/skills/governing-agents/scripts/registry.py check` | agent 注册表与生成物零漂移 |
| `python .agents/skills/governing-agents/scripts/registry.py audit` | 工作区归类与规范审计（发布前执行） |
| `python .agents/skills/verifying/scripts/verify/check_budgets.py` | 入口文档篇幅预算（发布前执行） |
| `python .agents/skills/verifying/scripts/verify/check_naming.py` | 目录与文件命名规范（发布前执行） |

README 的逐项验收清单见 `maintaining-readme` 的「验证清单」；CI 侧等价校验见 `.github/workflows/readme.yml`。

## 边界

- 统计卡与贡献图 SVG 由 CI（`snake.yml`）生成并发布到 `output` 分支，需要 token，不在本地生成或模拟，效果以线上产物为准。
- 全部校验通过后再交付；未经明确授权不执行 `git commit` 与 `git push`。
