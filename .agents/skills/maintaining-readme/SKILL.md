---
name: maintaining-readme
description: 维护 Quarto 源文件与生成的 README.md：渲染、预览、GitHub 兼容性校验，以及仓库布局、生成物与发布分支的维护入口。
metadata:
  short-description: Quarto 渲染与仓库维护规范
  summary: Quarto 渲染、预览、GitHub 兼容性校验与发布分支的维护入口
  triggers:
    - quarto
    - render
    - 预览
    - 发布
    - output 分支
    - 兼容性
    - 兼容
  paths:
    - "_quarto.yml"
    - "index.qmd"
    - ".github/workflows/**"
    - "scripts/**"
---

# Quarto README 维护规范

## 适用范围

适用于本仓库的源文件、渲染流程、生成物、目录布局与发布分支管理。

- 文案规则见 `writing-readme`，视觉资源与组件见 `designing-visuals`，入口文档写法见 `governing-agents`。
- 命名与落位、删改与重组的执行顺序见 `governing-agents`。
- 参考材料索引见 `.agents/knowledge/KNOWLEDGE.md`。
- 本技能内的参考：分支、发布与提交规范见 `references/repo-and-release.md`；目录检查清单见 `references/layout-checklist.md`。源文件、产物与分支等事实见 `.agents/knowledge/repo-layout/`（索引在 `KNOWLEDGE.md`）。

## 命名与目录

重组目录、重命名或新增文件前，先读 `governing-agents` 技能及其 `references/naming.md`、`references/structure.md`；改完在同一批次同步全部指针，并用 `references/layout-checklist.md` 逐项核对。

## 渲染与预览

- 修改后在仓库根目录执行 `quarto render` 生成 `README.md`。
- 本地预览执行 `quarto preview README.md --no-browser --no-watch-inputs`。
- 预览产物与 Agent 暂存文件只放根目录 `temp/`（已被 `.gitignore` 忽略），不散落在其他位置。
- 出现缓存、权限类报错时只清理 `.quarto/` 与 `.quarto-cache/` 后重新渲染，不删除源文件与受控资源。

## 动态资源边界

贡献图与统计卡由 `snake.yml` 在 CI 生成并发布到 `output` 分支，`quarto render` 只更新引用文字；不在本地生成或模拟这些 SVG，视觉效果以线上产物为准。

## GitHub 兼容性

- 输出保持 UTF-8、使用 GitHub Flavored Markdown；本地预览效果不能替代 GitHub 兼容性判断。
- 远程图片一律写成原始 HTML `<img src="...">`，不用 Markdown 图片语法，否则 Quarto 可能给带查询参数的地址追加扩展名。
- HTML 属性中的 `&` 写成 `&amp;`。
- 横幅是 `<picture>` 结构：WebP 作 `<source>`，静态 PNG 作 `<img>` 降级分支；需要跟随主题的资源用 `<picture>` 加 `prefers-color-scheme`。GitHub 官方图片格式清单里没有 WebP，因此降级分支必须保留。
- README 不能依赖 JavaScript；横幅动效由动画 WebP 本身承载。
- 组件来源限于 GitHub 官方托管资源与成熟公开徽章服务，清单见 `.agents/knowledge/component-trust/trust-tiers.md`；不引入第三方统计卡域名。

## 验证清单

- [ ] 根目录执行 `quarto render`，确认 `README.md` 已更新。
- [ ] 执行 `python .agents/skills/verifying/scripts/verify/check_readme.py`，结构断言全部通过。
- [ ] 再执行一次 `quarto render`，确认 `git diff --quiet README.md` 成立（渲染幂等）。
- [ ] `README.md` 第一行是横幅的 `<div align="center">`，顶部没有前导空行。
- [ ] 执行 `quarto preview README.md --no-browser --no-watch-inputs`，确认预览可用。
- [ ] `README.md` 是合法 UTF-8，所有 `<img>` 都带 `alt`，产物中没有 `data-align`。
- [ ] 标题符合 `writing-chinese` 的标题规范。
- [ ] 顶部 `<picture>` 含 WebP `<source>` 与带 `alt` 的静态降级 `<img>`；执行 `python .agents/skills/designing-visuals/scripts/media/gen_banner.py --check` 校验资源可解码、尺寸与时长正确。
- [ ] 用 `grep` 确认 `img.shields.io`、`opengraph.githubassets.com`、`raw.githubusercontent.com` 所在行没有被追加扩展名。
- [ ] 统计卡引用的是 `output` 分支的 `github-stats.svg`、`github-stats-dark.svg`、`github-languages.svg`、`github-languages-dark.svg`，没有引入第三方统计域名。
- [ ] 统计卡或贡献图显示空白时，先确认远端 `output` 分支是否存在对应 SVG，再检查 `snake.yml` 最近一次运行的「生成统计卡」与「检查动态资源完整」两步；`output` 资源缺失是运行时问题，本地 `quarto render` 无法暴露。
- [ ] 执行 `git diff --check`，确认 `git status` 中没有本地预览产物、`index.html` 或 `.zcodeignore`。
- [ ] 修改贡献图或统计卡生成脚本后，不在本地验证 SVG 效果，以 `output` 分支线上产物为准；验收以本清单的确定性检查为准。
- [ ] 涉及目录或命名改动时，按 `references/layout-checklist.md` 逐项核对。
- [ ] 需要确认 GitHub 远端状态时，先检测 `gh` 是否可用；不可用则改用 GitHub REST API（`curl`）与 `git ls-remote` 验证。
