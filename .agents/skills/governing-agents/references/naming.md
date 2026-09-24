# Agent 工作区命名规范

本规范适用于 `.agents/` 下的 `skills/`、`knowledge/`、`memory/`、`incidents/`，以及技能内部的 `scripts/`、`references/`、`assets/`。仓库目录结构规则见同技能下的 `references/structure.md`；两者冲突时，命名以本文件为准，结构以 `structure.md` 为准。

## 1. 核心原则

- **默认使用 kebab-case**：全小写字母 + 连字符 `-`。
- **固定入口文件使用大写**：`AGENTS.md`、`SKILL.md`、`KNOWLEDGE.md`、`MEMORY.md`、`README.md`。
- **日期使用 ISO 8601**：`YYYY-MM-DD`。
- **名称要有语义**：能看出「是什么」或「做什么」，避免 `utils`、`misc`、`temp`、`new`、`final`。
- **长度尽量短**：文件夹 ≤ 20 字符，文件名 ≤ 50 字符；技能目录名尤其遵守 ≤20。
- **字符集限制**：仅使用 `a-z`、`0-9`、`-`、`_`、`.`；避免空格、大写混合、特殊符号、重音字符。
- **禁止连续连字符**：`data--processor` 应写成 `data-processor`。
- **保持一致性**：同一层级、同一类资源使用同一种命名风格。

## 2. 文件夹命名方式

| 类型 | 规则 | 示例 | 反例 |
| :--- | :--- | :--- | :--- |
| 通用文件夹 | 小写 kebab-case，名词或动名词短语 | `visual-design`、`writing-readme` | `VisualDesign`、`visual_design` |
| 技能目录 | 动作 + 对象，kebab-case，≤20 字符 | `writing-readme`、`verifying`、`governing-agents` | `building-and-verifying`、`ReadmeContent` |
| 知识领域 | 领域名词，kebab-case | `visual-design`、`component-trust` | `VisualDesign`、`component_trust` |
| 记忆领域 | 领域名词，kebab-case | `media-build`、`quarto-render` | `MediaBuild`、`media_build` |
| 脚本目录 | 固定为 `scripts` | `scripts/` | `Scripts/`、`script/` |
| 参考目录 | 固定为 `references` | `references/` | `refs/`、`Reference/` |
| 资源目录 | 固定为 `assets` | `assets/` | `Assets/`、`static/` |

## 3. 文件命名方式

| 类型 | 规则 | 示例 | 反例 |
| :--- | :--- | :--- | :--- |
| 普通 Markdown | kebab-case + `.md` | `bright-palette.md`、`trust-tiers.md` | `BrightPalette.md`、`bright_palette.md` |
| 固定入口文件 | 大写，保持约定 | `AGENTS.md`、`SKILL.md`、`KNOWLEDGE.md`、`MEMORY.md` | `agents.md`、`skill.md` |
| 技能定义 | 固定为 `SKILL.md` | `SKILL.md` | `skill.md`、`Skill.md` |
| 知识索引 | 固定为 `KNOWLEDGE.md` | `KNOWLEDGE.md` | `knowledge.md` |
| 记忆索引 | 固定为 `MEMORY.md` | `MEMORY.md` | `memory.md`、`Memory.md` |
| 每日记忆 | `YYYY-MM-DD.md` | `2026-09-22.md` | `09-22-2026.md`、`2026_09_22.md` |
| 领域索引 | `<domain>/index.md` | `media-build/index.md` | `build_index.md`、`index-build.md` |
| 原子记忆 | `<domain>/<topic>.md` | `media-build/cache-missing.md` | `cache.md`、`cache_missing.md` |
| 技能内 Python（可 import） | snake_case `<action>_<target>.py` | `check_budgets.py`、`gen_banner.py` | `check-budgets.py` |
| 技能内 Shell | kebab-case `<action>-<target>.sh` | `deploy-site.sh` | `deploy_site.sh` |
| 模板/资源 | kebab-case + 扩展名 | `layout-checklist.md`、`logo.svg` | `LayoutChecklist.md`、`logo final.svg` |
| 版本文件 | `<name>-v<number>.md` 或 `<name>-<date>.md` | `banner-media-v2.md` | `banner-media-new.md`、`banner-media-final.md` |

## 4. 各目录命名约定

### 4.1 `.agents/skills/`

每个技能一个文件夹，文件夹名必须与 `SKILL.md` 中的 `name` 字段一致。

```text
.agents/skills/
├── verifying/
│   ├── SKILL.md
│   └── scripts/verify/
├── designing-visuals/
│   ├── SKILL.md
│   └── scripts/{media,activity,stats}/
├── writing-readme/
│   └── SKILL.md
├── writing-chinese/
│   ├── SKILL.md
│   └── references/
├── governing-agents/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── registry.py
│   └── references/
│       ├── naming.md
│       └── structure.md
└── maintaining-readme/
    ├── SKILL.md
    ├── scripts/filters/
    └── references/
        └── layout-checklist.md
```

- 技能目录名：短动作 + 对象，如 `writing-readme`、`verifying`（≤20）。
- 技能内可导入 Python：snake_case，如 `check_budgets.py`、`registry.py`。
- 技能内参考：`<topic>.md`，如 `layout-checklist.md`。
- 技能内资源：`<asset-name>.<ext>`，如 `report-template.md`。

### 4.2 `.agents/knowledge/`

按领域组织，入口文件为 `KNOWLEDGE.md`。

```text
.agents/knowledge/
├── KNOWLEDGE.md
├── visual-design/
│   ├── bright-palette.md
│   └── banner-media.md
├── component-trust/
│   └── trust-tiers.md
├── repo-layout/
│   ├── source-artifacts.md
│   ├── branches-workflows.md
│   └── publish-governance.md
└── local-env/
    └── python.md
```

- 领域目录：`<domain>`，如 `visual-design`、`component-trust`。
- 知识文件：`<topic>.md`，如 `bright-palette.md`。
- 索引文件：`KNOWLEDGE.md`。

### 4.3 `.agents/memory/`

采用三层索引：`MEMORY.md` → `domains/<domain>/index.md` → `domains/<domain>/<topic>.md`。

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

- 记忆总索引：`MEMORY.md`。
- 每日日志：`daily/` 下用 `YYYY-MM-DD.md`。
- 领域索引：`domains/<domain>/index.md`。
- 原子记忆：`domains/<domain>/<topic>.md`。

### 4.4 技能内 `scripts/`

可执行代码一律内聚在对应技能的 `scripts/`（对齐 Agent Skills / Codex / ADK / Copilot）。人与 CI 共用同一路径，从仓库根调用。

```text
scripts/
├── verify/                 # verifying 技能
│   ├── run_all.py
│   └── check_budgets.py
├── media/                  # designing-visuals 技能
│   ├── gen_banner.py
│   └── toolchain.py
└── registry.py             # governing-agents 技能（扁平叶子）
```

- 可 `import` 的 Python：snake_case。
- 仅 shell 的辅助脚本：kebab-case。
- 避免：`helper.sh`、`utils.py`、`script1.sh`。
- 不再使用根目录 `scripts/` 或 `.agents/tools/`。

## 5. 本仓库例外

以下例外由本仓库的 GitHub Profile + Quarto 形态决定，不视为违规：

1. **Quarto 约定文件保留原名**：`_quarto.yml`、`index.qmd`，以及 Quarto 可能生成的 `_freeze/` 等下划线前缀工具文件。
2. **根目录公开面**：`README.md`、`LICENSE`、`AGENTS.md` 与 `index.qmd`、`content/`、`assets/` 因 GitHub Profile 渲染和 Quarto 工程根必须留在根目录或一级目录。
3. **技能内 Python 用 snake_case**：`.agents/skills/*/scripts/` 下被 `import` 的模块及其同目录 CLI 兄弟文件统一 snake_case（PEP 8，kebab-case 无法被 `import`），例如 `toolchain.py`、`gen_banner.py`、`check_budgets.py`、`registry.py`。
4. **公开媒体文件名**：`assets/` 下的横幅资源用 kebab-case 加语义后缀，例如 `pixel-flower-landscape-64color.webp` 的 `-64color` 标明静态降级被减色到 64 色；后缀只为说明事实，不写 `-new`、`-final` 这类无信息词。

## 6. 可赋值命名模板

```text
.agents/
├── skills/
│   └── <skill-name>/          # ≤20 字符
│       ├── SKILL.md
│       ├── scripts/
│       │   └── <action>_<target>.py
│       ├── references/
│       │   └── <topic>.md
│       └── assets/
│           └── <asset-name>.<ext>
├── knowledge/
│   ├── KNOWLEDGE.md
│   └── <domain>/
│       └── <topic>.md
├── memory/
│   ├── MEMORY.md
│   ├── daily/
│   │   └── YYYY-MM-DD.md
│   └── domains/
│       └── <domain>/
│           ├── index.md
│           └── <topic>.md
└── incidents/
    ├── INDEX.md
    └── <domain>/
        └── <topic>.md
```

| 占位符 | 含义 | 示例 |
| :--- | :--- | :--- |
| `<skill-name>` | 短技能名 | `writing-readme`、`verifying`、`governing-agents` |
| `<action>` | 脚本动作 | `check`、`gen`、`add` |
| `<target>` | 脚本目标 | `budgets`、`banner`、`labels` |
| `<domain>` | 知识或记忆领域 | `visual-design`、`media-build`、`local-env` |
| `<topic>` | 具体主题 | `bright-palette`、`cache-missing`、`registry-pycache` |
| `<asset-name>` | 资源名称 | `layout-checklist`、`logo` |
| `<ext>` | 文件扩展名 | `md`、`svg`、`png` |
| `YYYY-MM-DD` | ISO 日期 | `2026-09-22` |

## 7. 检查清单

- [ ] 文件夹名是否全小写、用连字符分隔、且 ≤20 字符？
- [ ] 文件名是否遵循 kebab-case（Markdown）或 snake_case（可导入 Python）？
- [ ] 技能目录名是否与 `SKILL.md` 中的 `name` 一致？
- [ ] 日期文件是否使用 `YYYY-MM-DD.md`？
- [ ] 是否避免了空格、大写混合和特殊字符？
- [ ] 是否避免了 `utils`、`misc`、`temp`、`new`、`final` 等模糊名称？
- [ ] 是否避免了连续连字符（`--`）？
- [ ] 同一目录下同类资源的命名风格是否一致？
- [ ] 是否已废除根目录 `scripts/` 与 `.agents/tools/`？
