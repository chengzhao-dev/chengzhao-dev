# 目录与命名检查清单

重组目录、重命名文件或新增文件后逐项核对。规则原文见 `governing-agents/references/naming.md` 与 `governing-agents/references/structure.md`；执行顺序见 `governing-agents/references/refactor-flow.md`。

## 命名

- [ ] 文件夹名全小写、用连字符分隔（kebab-case）。
- [ ] 普通文件用 kebab-case；固定入口文件保持大写（`AGENTS.md`、`SKILL.md`、`KNOWLEDGE.md`、`MEMORY.md`、`README.md`、`index.md`）。
- [ ] 技能目录名与 `SKILL.md` 中的 `name` 一致，且为动名词形式。
- [ ] 页面片段文件名与对应章节一致，日期文件使用 `YYYY-MM-DD.md`。
- [ ] 没有空格、下划线、大写混合和特殊字符；没有连续连字符（`--`）。
- [ ] 没有 `utils`、`misc`、`temp`、`new`、`final` 等模糊名称。
- [ ] 同一目录下同类资源命名风格一致。

## 结构

- [ ] 性质相同的内容放在同一个文件夹。
- [ ] 具体内容文件位于二级或更深目录。
- [ ] 非叶子目录只放子文件夹与入口/索引文件。
- [ ] 叶子目录只放同一性质的最终文件。
- [ ] 根目录只放入口文件与 Quarto/公开面必需项（`README.md`、`ARCHITECTURE.md`、`LICENSE`、`index.qmd`、`_quarto.yml`、`config.toml`、`content/`、`assets/`、`scripts/`、`.agents/`、`.github/`）。
- [ ] 技能按 `SKILL.md`、`scripts/`、`references/`、`assets/` 拆分，不存在空目录。
- [ ] 知识按领域拆分为叶子目录，入口为 `KNOWLEDGE.md`。
- [ ] 记忆按 `MEMORY.md` → `domains/<domain>/index.md` → `<topic>.md` 拆分。
- [ ] 技能与入口文档都在 `governing-agents` 的篇幅预算内。

## 指针同步

- [ ] `AGENTS.md` 的导航指针指向真实路径。
- [ ] `.agents/README.md` 的技能清单与实际技能目录一致。
- [ ] `KNOWLEDGE.md` 索引与实际知识文件一致。
- [ ] `MEMORY.md` 与领域 `index.md` 指向实际记忆文件。
- [ ] 技能之间的交叉引用使用新的技能名。
- [ ] 全库检索不到旧路径（`tools/`、`_filters/`、根 `knowledge/`、`.agents/skills/designing-visuals/scripts/media/vendor/`）、旧片段名（`profile.md`、`projects.md`、`analytics.md`、`notes.md`）与旧技能名。
