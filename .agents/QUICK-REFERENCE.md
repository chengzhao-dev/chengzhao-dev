<!-- 本文件由 .agents/skills/governing-agents/scripts/registry.py 生成，勿手改；手改会被 check 判为漂移。 -->

# 检索速查表

先在本表定位条目再读正文；定位不到时运行
`python .agents/skills/governing-agents/scripts/registry.py search <关键词>` 粗筛；
查「哪些文档指向某文件」或搜正文用 `python .agents/skills/governing-agents/scripts/registry.py lookup <关键词>`。

## 技能（skill）

| 名称 | 摘要 | 触发词 | 路径 |
| :--- | :--- | :--- | :--- |
| designing-visuals | 横幅、色板、Shields 组件与推荐项目列表样式的唯一标准 | 横幅、色板、徽章、组件、视觉、推荐项目、picture | `.agents/skills/designing-visuals/SKILL.md` |
| governing-agents | agent 工作区治理：入口文档写法与篇幅预算、删合拆重构、目录命名、技能拆分合并与内容归类 | 重构、精简、合并、拆分、命名、目录、归类、指针、AGENTS 文档、篇幅预算、技能 | `.agents/skills/governing-agents/SKILL.md` |
| maintaining-readme | Quarto 渲染、预览、GitHub 兼容性校验与发布分支的维护入口 | quarto、render、预览、发布、output 分支、兼容性、兼容 | `.agents/skills/maintaining-readme/SKILL.md` |
| verifying | Quarto 渲染与全套本地校验命令的统一入口 | 构建、校验、渲染、verify、check、audit | `.agents/skills/verifying/SKILL.md` |
| writing-chinese | 中文表达、代码命名与注释的唯一规范，注释格式语法在 references/comment-format.md | 中文、写作、措辞、标题、标点、命名、注释 | `.agents/skills/writing-chinese/SKILL.md` |
| writing-readme | Profile README 的文案、事实核验、章节结构与字数区间唯一标准 | README、文案、字数、章节、alt、事实核验 | `.agents/skills/writing-readme/SKILL.md` |

## 入口（entrypoint）

| 名称 | 摘要 | 触发词 | 路径 |
| :--- | :--- | :--- | :--- |
| AGENTS | 硬性约束与执行原则，任务开始前必读 | 硬约束、红线、构建命令、执行原则 | `AGENTS.md` |
| ARCHITECTURE | 项目结构、目录职责与常用流程图 | 结构、目录、流程图、新人入门 | `ARCHITECTURE.md` |
| agents-workspace | agent 工作区三区职责与归类判断规则 | 归类、放哪、工作区、技能规则 | `.agents/README.md` |
| knowledge | 知识库索引：事实与参数 | — | `.agents/knowledge/KNOWLEDGE.md` |
| memory | 记忆索引：跨会话经验 | — | `.agents/memory/MEMORY.md` |

## 知识（knowledge）

| 名称 | 摘要 | 触发词 | 路径 |
| :--- | :--- | :--- | :--- |
| trust-tiers | 允许与禁止引用的外部资源清单及四级判定方法 | 组件、信任、shields、统计卡、第三方、禁止 | `.agents/knowledge/component-trust/trust-tiers.md` |
| local-python | 本机 Python 解释器位置与统一用法，唯一事实源是 config.toml 的 python 字段 | python、解释器、miniforge、conda、环境、Store 占位、本机工具、shebang | `.agents/knowledge/local-env/python.md` |
| branches-workflows | output 分支六个 SVG、工作流分工与 .gitignore 必须保持的忽略清单 | output 分支、snake.yml、readme.yml、svg、gitignore、工作流、生成顺序 | `.agents/knowledge/repo-layout/branches-workflows.md` |
| publish-governance | 公开内容的来源、生成物、隐私与静态校验边界 | GitHub、发布面、隐私扫描、生成物、静态链接、唯一事实源 | `.agents/knowledge/repo-layout/publish-governance.md` |
| source-artifacts | 仓库目录职责、Quarto 配置事实与 FFmpeg/FFprobe 五级解析顺序 | 源文件、产物、toolchain、ffmpeg、config.toml、_quarto.yml、目录职责 | `.agents/knowledge/repo-layout/source-artifacts.md` |
| banner-media | 横幅 WebP/静态降级的素材规格、编码参数、体积上限与重新生成入口 | 横幅、banner、webp、ffmpeg、64color、体积上限 | `.agents/knowledge/visual-design/banner-media.md` |
| bright-palette | 浅色/深色主题色板 token 与 Shields 参数示例 | 色板、色值、token、配色、shields | `.agents/knowledge/visual-design/bright-palette.md` |

## 记忆（memory）

| 名称 | 摘要 | 触发词 | 路径 |
| :--- | :--- | :--- | :--- |
| cursor-attribution | Cursor 自动注入的共著 trailer 会让 cursoragent 出现在 Contributors，去除与预防方法 | Cursor、cursoragent、Contributors、Co-authored-by、attribution、共著、提交信息、归属 | `.agents/memory/domains/agent-workspace/cursor-attribution.md` |
| incidents-design | incidents 与 memory 的边界、平时不可见的豁免机制、检索方案选型理由 | incidents、事故、案例库、错误案例、检索方案、索引 | `.agents/memory/domains/agent-workspace/incidents-design.md` |
| plan-doc-location | 计划/审计文档放 .agents/plan/，根目录白名单由 check_naming.py 拦截 | 计划文档、审计报告、根目录、temp、白名单 | `.agents/memory/domains/agent-workspace/plan-doc-location.md` |
| progressive-nav | 人类阅读优先、Agent 路由其次的文档重构选择与边界 | 渐进式导航、双入口、文档重构、平衡清理、信息架构 | `.agents/memory/domains/agent-workspace/progressive-nav.md` |
| registry-benchmark | 检索效果评测结论（token/命中/耗时）与生成物保持 .agents/ 根的决策记录 | 注册表、registry、检索效果、benchmark、token、命中率、lookup、生成物位置 | `.agents/memory/domains/agent-workspace/registry-benchmark.md` |
| stale-project-cache | 渲染无报错但产物过期的根因与清缓存处理步骤 | 缓存、project-cache、deno-kv、渲染错误、过滤器未生效 | `.agents/memory/domains/quarto-render/stale-project-cache.md` |
| verify-approach | 验收以静态校验为准（无截图）的决策由来，现行清单见技能 | 验收、截图、静态校验、幂等、决策 | `.agents/memory/domains/quarto-render/verify-approach.md` |
