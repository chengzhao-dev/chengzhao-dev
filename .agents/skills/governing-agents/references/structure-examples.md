# 结构示例与性质判断

structure.md 的配套示例：如何判断「性质相同」，以及各区域的标准封装布局。
规则原文见同目录 `structure.md`，冲突时以规则文件为准。

## 1. 如何判断「性质相同」

满足以下任意一条或多条，就可以认为它们性质相同，适合放进同一个文件夹：

- 属于同一领域，如 `visual-design`、`component-trust`。
- 服务于同一技能，如 `maintaining-readme` 下的所有参考。
- 具有同一职责，如 `tools`、`scripts`、`references`、`assets`。
- 面向同一读者，如给 Agent 的指令、给人类的文档、给工具的脚本。
- 生命周期与格式一致，如每日流水账、全部是 Lua 过滤器。
- 可以共享同一个入口文件或索引文件。

## 2. 各区域封装示例

### 2.1 `skills/` 技能封装

一个技能一个文件夹，技能内部按资源性质继续拆分。

```text
.agents/skills/
├── writing-chinese/
│   ├── SKILL.md
│   └── references/
│       ├── comment-format.md
│       └── standards-sources.md
├── verifying/
│   └── SKILL.md
├── writing-readme/
│   └── SKILL.md
├── designing-visuals/
│   └── SKILL.md
├── governing-agents/
│   ├── SKILL.md
│   └── references/
│       ├── naming.md
│       └── structure.md
└── maintaining-readme/
    ├── SKILL.md
    ├── scripts/filters/
    │   └── github-align.lua
    └── references/
        ├── repo-and-release.md
        └── layout-checklist.md
```

规则：

- 技能目录名与 `SKILL.md` 中的 `name` 一致。
- `SKILL.md` 放在技能目录根部。
- 脚本放 `scripts/`，参考文档放 `references/`，模板和静态资源放 `assets/`；某类资源不存在时不必建空目录。
- 如果某类资源继续增多，可在其下再按主题拆子目录。

### 2.2 `knowledge/` 知识封装

按领域组织，入口是 `KNOWLEDGE.md`。

```text
.agents/knowledge/
├── KNOWLEDGE.md
├── visual-design/
│   ├── bright-palette.md
│   └── banner-media.md
├── component-trust/
│   └── trust-tiers.md
└── local-env/
    └── python.md
```

规则：

- `KNOWLEDGE.md` 是知识库入口/索引。
- 每个领域一个文件夹。
- 如果领域内还有子领域，领域文件夹只放 `index.md` 和子文件夹。
- 具体知识文件放在叶子目录中。

### 2.3 `memory/` 记忆封装

采用「总索引 → 领域 → 具体记忆」的结构。

```text
.agents/memory/
├── MEMORY.md
├── daily/
│   └── 2026-09-22.md
└── domains/
    └── media-build/
        ├── index.md
        └── cache-missing.md
```

规则：

- `MEMORY.md` 是记忆总索引，尽量精简。
- `daily/` 放每日流水账，不自动注入，按需查询。
- `domains/` 下按领域封装，每个领域目录内放 `index.md` 作为领域索引。
- 具体记忆文件放在领域叶子目录中。

### 2.4 技能 `scripts/` 与生成物

- 可执行自动化一律放在 `.agents/skills/<技能>/scripts/`；注册表、检索、审计在 `governing-agents/scripts/`。
- 生成物 `registry.json` 与 `QUICK-REFERENCE.md` 放 `.agents/` 一级，文件头标注「由脚本生成，勿手改」。
- 改动任何 `.agents/` 内容后重跑 `python .agents/skills/governing-agents/scripts/registry.py build`，保持生成物零漂移。


## 扩展约定

- 更大项目按同样模式继续拆：每个区域一个三级目录，领域内再按主题拆四级叶子文件。
- 新增区域示例时追加到本文件对应小节，单文件超出篇幅预算就再按区域拆新参考文件。
