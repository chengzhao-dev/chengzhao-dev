---
name: governing-agents
description: 治理 agent 工作区：撰写或精简 AGENTS 类入口文档（AGENTS.md、ARCHITECTURE.md、.agents/README.md、KNOWLEDGE.md、MEMORY.md）、判断删合拆与重构顺序、决定目录与命名、合并小技能、归类新增内容、同步索引指针时使用。
metadata:
  short-description: agent 工作区治理唯一技能
  summary: agent 工作区治理：入口文档写法与篇幅预算、删合拆重构、目录命名、技能拆分合并与内容归类
  triggers:
    - 重构
    - 精简
    - 合并
    - 拆分
    - 命名
    - 目录
    - 归类
    - 指针
    - AGENTS 文档
    - 篇幅预算
    - 技能
  paths:
    - "AGENTS.md"
    - ".agents/**"
---

# Agent 工作区治理

## 适用范围

治理 `.agents/`（skills、knowledge、memory、incidents）与全部入口文档：本技能管「放哪里、叫什么名字、要不要删合拆、按什么顺序动、写多长」，由原 `organizing-agent-workspace`、`refactoring-project-structure`、`writing-agent-docs` 三个技能合并而成。

边界：中文措辞与注释见 `writing-chinese`；README 文案与字数区间见 `writing-readme`；视觉组件见 `designing-visuals`；渲染、预览与发布见 `maintaining-readme`。

## 内容归类规则

新增或整理内容时，先按性质判断归属，再动手：

| 内容性质 | 归属 |
| :--- | :--- |
| 可复用流程与步骤（how） | `.agents/skills/<技能>/SKILL.md` |
| 事实与参数（what，如色值、来源清单、环境参数） | `.agents/knowledge/<领域>/<主题>.md` |
| 跨会话经验教训（踩坑现象 → 根因 → 对策） | `.agents/memory/domains/<领域>/<主题>.md` |
| 错误案例与事故复盘（需平时不可见、排查时检索） | `.agents/incidents/<领域>/<主题>.md` |
| 硬性约束与执行原则 | 根目录 `AGENTS.md` |
| 项目结构、流程图、新人入门 | 根目录 `ARCHITECTURE.md` |
| 随技能使用的长参考 | 技能内 `references/` |
| agent 生成的计划、审计、批次报告（需长期可审计） | `.agents/plan/` |
| agent 一次性草稿与中间产物（可丢弃） | 根目录 `temp/`（不入库） |

- 一条内容只归一类；「规则 + 参数」并存时规则放技能、参数下沉知识，技能内留指针。
- memory 与 incidents 的边界：一般踩坑经验（下次同类任务就该知道）进 `memory`；要求「平时任务当不存在、排查失败时才按症状检索」的事故复盘进 `incidents`。判断标准是读取时机，不是内容类型。
- incidents 目录的约定：`incidents/INDEX.md` 是唯一索引（领域 → 症状关键词 → 案例路径），整个目录（含 INDEX.md）不进 `registry.json` 与 `QUICK-REFERENCE`，只在 `AGENTS.md` 留一条排查入口；新增案例后必须同步 INDEX.md，`registry.py audit` 校验双向一致。
- 入库条目的 frontmatter 必须带 `metadata.triggers` 与 `metadata.summary`，否则 `audit` 告警；新增、移动或改名后重跑 `python .agents/skills/governing-agents/scripts/registry.py build`，并同步各索引的指针。

## 技能拆分与合并规则

- 触发信号：技能总数超过 10；某技能只有 1–2 个文件且与另一技能职责相近；两个技能总被同一任务同时引用；某技能长期零触发（`audit` 可辅助判断）。
- 合并判断：读者、更新频率与任务链相近即性质相近，合并为一个更广的技能；合并时可改目录名与 `name`，把原正文重组为新技能的章节或 `references/`，消掉重复段落，不得简单拼接。
- 拆分判断：技能超出篇幅预算，或同时服务两类读者时，先把长参考拆到 `references/`，仍超预算再拆技能。
- 合并后义务：更新 `.agents/README.md` 技能表与全部交叉引用；同步 `.agents/skills/verifying/scripts/verify/check_budgets.py` 依赖的预算表路径；重跑 `build`；全库检索旧技能名确认零残留。

## 篇幅预算

| 文件 | 行数上限 | token 上限 |
| :--- | :--- | :--- |
| `AGENTS.md` | 60 | 1600 |
| `.agents/README.md` | 30 | 700 |
| `KNOWLEDGE.md`、`MEMORY.md` | 25 | 600 |
| `memory/domains/<domain>/index.md` | 20 | 500 |
| `knowledge/`、`memory/` 下其他条目文件 | 110 | 2400 |
| 单个 `SKILL.md` | 220 | 2000 |
| 技能内 `references/*.md` | 300 | 3200 |
| `.agents/plan/*.md` | 300 | 3200 |
| `.agents/incidents/INDEX.md` | 40 | 900 |
| `.agents/incidents/<domain>/*.md` | 300 | 3200 |
| `.agents/QUICK-REFERENCE.md`（生成物，随条目数增长） | 70 | 1800 |

行数含空行；token 按「中文 1 字 ≈ 1 token」粗算。超出预算时把细节下沉到技能 `references/`、`knowledge/` 或 `memory/`，不删硬性约束；`registry.json` 是机器生成物，不做篇幅预算。校验命令：`python .agents/skills/verifying/scripts/verify/check_budgets.py`。

依据（2026-09 核实）：AGENTS.md 规范要求 README 面向人类、AGENTS.md 面向 agent（<https://agents.md/>）；Anthropic Agent Skills 要求 SKILL.md ≤500 行、细节渐进披露下沉（<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>）。本表更严格，冲突时以本表为准。

## 细节参考

- 渐进式导航、中心—流程—细节—参考的阅读结构与去重判断：`references/progressive-nav.md`。
- 入口文档的写法约束、适用边界与检查清单：`references/entry-docs.md`。
- 删合拆的触发信号、三类判断、唯一事实源归属、执行顺序、必须保留项与验收清单：`references/refactor-flow.md`。
- 目录与命名的规则原文、重组流程与检查清单：`references/naming.md`、`references/structure.md`（重组流程见 structure.md 第 4 节）。
- 性质判断与各区域封装示例（随项目规模扩展）：`references/structure-examples.md`。

## 检查清单

- [ ] 每个文件都在「篇幅预算」内。
- [ ] 入口文档开篇有定位段（这是什么、为什么存在），且没有历史、进度、流水账动机与举例；技能已有的内容只以指针出现。
- [ ] 同一事实全仓只在一处完整定义，其余是指针。
- [ ] 新增条目的 frontmatter 带 `metadata.triggers` 与 `metadata.summary`。
- [ ] `registry.py check` 与 `audit` 均通过，QUICK-REFERENCE 已重建。
- [ ] 入口文档与注册表的指针全部指向真实路径。
