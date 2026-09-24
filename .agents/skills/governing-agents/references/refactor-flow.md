# 重构流程

用于对已有内容做「删、合、拆」与结构调整：文档、技能、页面片段与脚本。本技能管「要不要动、按什么顺序动」；命名与落位见 `references/naming.md` 与 `references/structure.md`；入口文档写法见 `references/entry-docs.md`；渲染、发布与提交见 `maintaining-readme`。

## 触发信号

出现任一条即按本文件执行：

- 同一事实在 2 处以上各写一遍，且已经开始不同步。
- 单个文档超出 `SKILL.md` 的篇幅预算。
- 同一目录下文件超过 7 个，或文件名与内容不再对应。
- 新人读完入口文档仍不知道该看哪个文件。
- 需要写一段说明才能解释某个文件或目录的用途。

## 三类判断

### 删

- 事实无法验证（失效链接、空仓库、查不到的数据）直接删除，不留占位描述。
- 只服务一次性讨论、没有复用价值的临时说明直接删除。
- 与其他位置完全重复、且不是唯一事实源的内容删除，保留指针。
- 不确定能否删除时先提示，不擅自删除预存在的历史文件与死代码。

### 合

- 多个小文件合并后仍在一份文档的篇幅预算内，且读者与更新频率一致时合并。
- 合并后必须消掉重复段落，不能是两段内容的简单拼接。
- 职责不同的内容不合并：「写什么」与「怎么写」、命名规则与结构规则分别独立。

### 拆

- 单个文件超出篇幅预算，或同时服务两类读者、包含两种格式时拆分。
- 长参考下沉到技能内 `references/`；事实与参数放 `knowledge/`；跨会话经验放 `memory/`。
- 拆分后每份文件仍要能独立回答一个问题。

## 唯一事实源

- 每条规范只在一个文件里写完整内容，其他位置只写指针。
- 现有归属：README 字数区间与结构 → `writing-readme`；推荐项目样式 → `designing-visuals`；中文措辞、标题、命名与注释 → `writing-chinese`（格式语法在其 `references/comment-format.md`）；入口文档写法、篇幅预算、重构顺序、目录命名、技能合并与归类 → 本技能；渲染与发布 → `maintaining-readme`。
- 发现同一规则出现在两处时，保留信息更完整的一处，另一处改成指针。

## 执行顺序

1. 列出改动范围与唯一事实源归属，先写清哪一处保留、哪些改成指针。
2. 先改内容（文案、规范），后动结构（移动、改名）；内容未定稿不搬文件。
3. 移动或改名后，在同一批次同步全部指针。
4. 重新生成生成物（`quarto render`、`registry.py build`），确认与源文件一致。
5. 全库检索旧路径、旧文件名、旧技能名与旧数字，确认没有残留。
6. 按 `references/naming.md` 第 7 节与 `references/structure.md` 第 6 节的检查清单逐项核对。

## 必须保留项

- `README.md` 只能由 Quarto 生成，禁止手改。
- 横幅的「WebP `<source>` + 带 `alt` 的 PNG 降级 `<img>`」`<picture>` 结构。
- `_templates/readme.markdown` 与仍在使用的 Quarto 过滤器（当前仅 `.agents/skills/maintaining-readme/scripts/filters/github-align.lua`）。
- CI 断言引用的路径与资源：`readme.yml` 校验的横幅资源、源素材与生成脚本。
- `AGENTS.md` 中的硬性约束与隐私红线，不因精简而删除。
- `.agents/skills/governing-agents/scripts/registry.py` 及其生成物 `registry.json`、`QUICK-REFERENCE.md`。

## 验收清单

- [ ] 每条规范只有一个完整定义处，其余位置是指针。
- [ ] 所有入口文档都在篇幅预算内。
- [ ] `quarto render` 后生成物与源文件一致，`registry.py check` 通过，没有意外 diff。
- [ ] 全库检索不到旧路径、旧文件名、旧技能名与旧数字。
- [ ] 目录与命名符合 `references/naming.md` 与 `references/structure.md` 的检查清单。
- [ ] 没有删除硬性约束、CI 依赖的资源、受控脚本与注册表工具。
- [ ] 暂存草稿只出现在根目录 `temp/`；计划/审计类会话文档只出现在 `.agents/plan/`；根目录无其他 agent 产物残留（`check_naming.py` 根目录白名单通过）。
