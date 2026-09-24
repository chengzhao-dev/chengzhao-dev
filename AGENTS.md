# Agent 工作规范

本仓库用 Quarto 生成 GitHub Profile README。Agent 先遵守本文件，再按任务读取技能、知识与记忆；项目地图见 [`ARCHITECTURE.md`](ARCHITECTURE.md)。

## 任务起点

1. 读取 `.agents/memory/MEMORY.md`，了解已知坑点。
2. 在 `.agents/QUICK-REFERENCE.md` 定位技能；找不到时使用注册表搜索。
3. 需要稳定参数时读取 `.agents/knowledge/KNOWLEDGE.md` 的对应条目。
4. 涉及删改、改名、归类或入口设计时，先读取 `governing-agents`。
5. 排查失败或行为异常时，先查 `.agents/incidents/INDEX.md`，命中相似症状再读对应案例；其他任务把该目录当作不存在，不读取。

## 不可违反的规则

- 中文是主要语言；项目名、协议名、技术术语与代码标识保留英文。
- emoji 只用于最终生成的 `README.md` 展示内容；README 的内容源 `index.qmd` 与 `content/` 可以携带展示 emoji，入口文档、`.agents/`、脚本、配置和 CI 文本不新增 emoji。
- `README.md` 只能由 Quarto 生成；`assets/banner/` 资源只能由脚本生成。
- 横幅必须保留 WebP `<source>` 与带 `alt` 的 PNG 降级 `<img>`。
- 只展示可验证的技术栈、项目和数据；无法确认的内容先修复，修复不了就删除。
- 组件只允许 GitHub 官方托管资源与 Shields.io；不引入第三方统计卡或动态图服务。
- 不添加 OpenAI SDK、API Key、密钥文件或与 Profile README 无关的运行时代码。
- 不提交 Quarto 缓存、本地构建产物或 Agent 暂存文件；一次性草稿放根目录 `temp/`（不入库），计划、审计与批次报告放 `.agents/plan/`（随仓库提交）；根目录不得新增其他 agent 产物。
- `_templates/` 是正式输出模板，不能删除或移动到 `temp/`。
- 提交信息与作者身份不得出现 Cursor 归属：不写 `Co-authored-by: Cursor`，不出现 `cursoragent@cursor.com`，不把 Cursor 写为 author/committer；agent 代写提交信息时主动移除，本机在 Cursor 设置里关闭 Attribution。
- 未经明确授权不执行 `git commit` 与 `git push`。

## 隐私与发布红线

- 密钥、token、`.env`、凭证、私钥、个人绝对路径、未公开邮箱或电话不得进入 Git、README、`.agents/` 或 CI 产物。
- 不含密钥信息的纯工具配置路径（如 Python 解释器、FFmpeg 位置）不视为隐私，可写入 `config.toml` 或知识条目；用户主目录下可识别个人的路径仍按敏感处理。
- 发现疑似敏感内容时按敏感处理，先停止扩散并指出来源。
- GitHub 发布面的静态边界见 `.agents/knowledge/repo-layout/publish-governance.md`。

## 执行边界

- 构建、预览与校验只按 `verifying` 技能执行。
- README 文案按 `writing-readme`，视觉资源按 `designing-visuals`。
- 中文措辞、命名与注释按 `writing-chinese`。
- 本机工具配置只看根目录 `config.toml`；不得把本机路径写入受控文件。
