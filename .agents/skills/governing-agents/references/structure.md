# Agent 工作区结构规范

本规范适用于项目根目录、`.agents/` 及其下的 `skills/`、`knowledge/`、`memory/`、`incidents/`，以及技能内部资源目录。配套命名规范见同技能下的 `references/naming.md`；两者冲突时，命名以 `naming.md` 为准，结构以本文件为准。

## 1. 目标

- 把**性质相同**的内容放进同一个文件夹。
- 尽量使用**从项目根目录算起的二级或更深目录**来封装文件。
- 让每个目录的职责单一、可预测、方便查找和理解。
- 让 Agent 能通过「注册表 + 按需加载」快速定位内容，而不是扫描大量散乱文件。

## 2. 核心规则

### 2.1 按性质封装

一个文件夹只封装一种「性质」的内容。性质可以按以下维度判断：

- **领域**：如 `visual-design`、`component-trust`。
- **职责**：如 `scripts`、`references`、`assets`。
- **技能**：如 `writing-readme`、`maintaining-readme`、`verifying`。
- **生命周期**：如 `daily`、`domains`。
- **读者/用途**：如 Agent 指令、人类文档、工具脚本、模板资源。
- **格式**：如 Markdown、Lua、Python、图片。

如果同一目录下出现两种以上性质，就继续拆成子文件夹。

### 2.2 尽量使用二级或更深目录

从项目根目录算起，具体内容文件尽量放在**二级或更深目录**中。

```text
chengzhao-dev/
├── AGENTS.md                         # 根目录入口文件，允许
├── README.md                         # 根目录入口文件，允许
└── .agents/                          # 一级：Agent 工作区
    ├── README.md                     # 一级入口文件，允许
    ├── skills/                       # 二级：技能总目录
    │   ├── governing-agents/         # 三级：具体技能
    │   │   ├── SKILL.md              # 技能入口文件，允许
    │   │   ├── scripts/              # 四级：技能脚本（注册表等）
    │   │   │   └── registry.py
    │   │   └── references/           # 四级：技能参考
    │   │       ├── naming.md
    │   │       └── structure.md
    │   └── maintaining-readme/       # 三级：具体技能
    │       ├── SKILL.md
    │       ├── scripts/filters/      # Quarto 过滤器
    │       └── references/
    ├── knowledge/                    # 二级：知识总目录
    │   ├── KNOWLEDGE.md
    │   └── visual-design/
    │       └── bright-palette.md
    ├── memory/                       # 二级：记忆总目录
    │   ├── MEMORY.md
    │   └── domains/
    │       └── quarto-render/
    │           ├── index.md
    │           └── stale-project-cache.md
    └── incidents/                    # 二级：事故案例（平时不可见，排查时检索）
        ├── INDEX.md
        └── agent-workspace/
            └── registry-pycache.md
```

不推荐：把具体文件平铺在根目录或一级目录，性质混杂，Agent 难以判断加载顺序和归属。

### 2.3 非叶子目录不直接放具体内容文件

每个目录（包括根目录）除非它是**相对于当前路径的最后一级目录**，也就是里面已经没有子文件夹，否则不要直接堆放具体内容文件。

- **非叶子目录**：还有子文件夹的目录。只放：
  - 固定入口文件：`AGENTS.md`、`SKILL.md`、`KNOWLEDGE.md`、`MEMORY.md`、`README.md`、`index.md`。
  - 子文件夹。
  - 必要的轻量索引文件。
- **叶子目录**：没有子文件夹的目录。直接放该性质的最终文件。

唯一例外是 `.agents/` 一级下的两个注册表生成物：`registry.json` 与 `QUICK-REFERENCE.md` 由 `skills/governing-agents/scripts/registry.py` 生成，供检索一步定位，属于「工具产物」性质，不拆子目录。

### 2.4 本仓库根目录与公开面

GitHub Profile README 与 Quarto 工程对本仓库的根目录有硬性要求，因此根目录放宽为「只放入口文件 + Quarto/公开面必需项」：

```text
chengzhao-dev/
├── AGENTS.md            # 入口
├── README.md            # 入口（由 Quarto 生成）
├── ARCHITECTURE.md      # 入口（项目说明：流程图、目录树与常用流程）
├── LICENSE              # 公开面必需
├── .gitattributes       # 行尾与 diff 属性
├── index.qmd            # Quarto 工程根
├── _quarto.yml          # Quarto 工程根
├── _templates/          # Quarto 输出模板（最小模板消除 README 前导空行）
├── config.toml           # 唯一的项目工具配置（Python、FFmpeg、工具缓存目录）
├── content/             # 页面 Markdown 片段
├── assets/              # 公开媒体（README 直接引用）
│   ├── banner/          # 叶子：README 引用的横幅 WebP 与静态降级 PNG
│   └── source/          # 叶子：可再生的横幅原始素材
├── .agents/             # Agent 工作区（技能 scripts、计划/审计放 .agents/plan/）
├── .github/             # 仓库自动化配置
└── .gitignore
```

- 根目录封闭清单：上表即全部允许项，另加被 `.gitignore` 忽略的 `temp/`、`.quarto/`、`.zcode/`、`.zcodeignore`；计划/审计类会话文档放 `.agents/plan/`，一次性草稿放 `temp/`，均不落根目录，`check_naming.py` 白名单按此拦截。
- 可执行自动化一律放在 `.agents/skills/<技能>/scripts/`（人与 CI 共用同一路径）；不再保留根目录 `scripts/` 或 `.agents/tools/`。
- `content/`、`assets/banner/`、`assets/source/` 的子目录已是叶子目录，具体文件直接放入。
- 本仓库不做 Quarto 站点化改造，因此不把 `index.qmd` 收进 `site/` 之类的子目录。

## 4. 拆分与重组流程

当目录开始混乱时，按以下步骤处理：

1. **列出文件**：列出目标目录下所有文件和子目录。
2. **标记性质**：为每个文件标记领域、职责、生命周期、格式等性质。
3. **分组**：把性质相同的文件归为一组。
4. **命名文件夹**：按 `references/naming.md` 用 kebab-case 命名文件夹。
   - 技能目录：动作 + 对象，如 `writing-readme`、`verifying`（≤20 字符）。
   - 知识领域：领域名词，如 `visual-design`、`component-trust`。
   - 资源目录：固定名称，如 `scripts`、`references`、`assets`。
   - 记忆领域：领域名词，如 `media-build`、`quarto-render`。
5. **移动文件**：把文件移入对应文件夹。
6. **继续拆分**：如果新文件夹内仍有多种性质，继续拆分子文件夹。
7. **更新入口**：更新 `AGENTS.md`、`KNOWLEDGE.md`、`MEMORY.md`、`SKILL.md` 中的指针或索引，重跑 `registry.py build`。
8. **检查命名与层级**：确认符合 `references/naming.md` 和本文件规则。

### 拆分信号

出现以下情况时，说明应该拆分：

- 同一目录下文件超过 **7 个**。
- 多个文件名有共同前缀，如 `banner-*.md`。
- 需要写一段说明才能解释目录内容。
- 文件更新频率差异很大。
- 查找某个文件时需要反复滚动或搜索。

## 5. 检查清单

- [ ] 性质相同的内容是否放在同一个文件夹？
- [ ] 具体内容文件是否尽量位于二级或更深目录？
- [ ] 非叶子目录是否只放子文件夹和入口/索引文件？
- [ ] 叶子目录是否只放同一性质的最终文件？
- [ ] 根目录是否只放入口文件与 Quarto/公开面必需项？
- [ ] 技能是否按 `SKILL.md`、`scripts/`、`references/`、`assets/` 拆分？
- [ ] 知识是否按领域和子领域拆分？
- [ ] 记忆是否按总索引、领域、具体记忆拆分？
- [ ] 生成物是否已重建且头注标注「勿手改」？
- [ ] 文件夹和文件命名是否符合 `references/naming.md`？
- [ ] 是否避免了 `utils`、`misc`、`temp`、`new`、`final` 等模糊名称？
- [ ] 是否更新了 `AGENTS.md`、`KNOWLEDGE.md`、`MEMORY.md`、`SKILL.md` 中的索引或指针？
