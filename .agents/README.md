# Agent 工作区

这里保存仓库级 Agent 资源。按任务选择 `skill`、`knowledge` 或 `memory`，再读取对应正文；项目地图见 [`ARCHITECTURE.md`](../ARCHITECTURE.md)，硬性规则见 [`AGENTS.md`](../AGENTS.md)。

## 先找哪一类

| 你要找什么 | 先读哪里 |
| :--- | :--- |
| 如何执行构建、写作或重构 | `skills/<name>/SKILL.md` |
| 当前参数、路径和来源 | `knowledge/KNOWLEDGE.md` |
| 历史问题、决策和经验 | `memory/MEMORY.md` |
| 按关键词定位资源 | `QUICK-REFERENCE.md` |

## 三类资源

- `skills/`：可复用流程，回答“怎么做”。
- `knowledge/`：稳定事实与参数，回答“当前是什么”。
- `memory/`：跨会话经验，回答“过去哪里容易出错”。

## 生成物与维护

- `skills/governing-agents/scripts/registry.py` 扫描正文和 frontmatter，生成 `registry.json`、`QUICK-REFERENCE.md`；两者禁止手改。
- 正文是唯一事实源，索引只负责定位；同一规则不要在多个入口完整复制。
- 新增、移动或改名后，按 `governing-agents` 的归类、命名和篇幅规则同步索引。
- 文档采用“定位 → 找路 → 地图 → 执行 → 深入”的渐进式结构，规范见 `skills/governing-agents/references/progressive-nav.md`。
