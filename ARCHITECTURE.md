# 项目总览

这是 chengzhao-dev 的 GitHub Profile README 源代码与自动化工程。访客看到的是 Quarto 生成的 `README.md`；维护者修改源文件后，由 GitHub Actions 负责校验，并定期更新贡献图和统计卡等动态资源。

`index.qmd` 组织 `content/` 下的页面片段，`README.md` 是对外生成物，动态 SVG 发布到 `output` 分支。新人只需按任务进入对应源文件，不必通读整个仓库。

## 先从任务开始

| 你要做什么 | 先看哪里 | 完成后检查 |
| :--- | :--- | :--- |
| 修改主页文案或章节顺序 | `content/`、`index.qmd` | `maintaining-readme` |
| 修改横幅视觉 | `assets/source/`、`.agents/skills/designing-visuals/scripts/media/` | `designing-visuals` |
| 修改贡献图或统计卡 | `.agents/skills/designing-visuals/scripts/activity/`、`.agents/skills/designing-visuals/scripts/stats/`、`.github/workflows/snake.yml` | 动态资源校验 |
| 修改 Agent 规则或工作区 | `AGENTS.md`、`.agents/` | `governing-agents`、注册表检查 |
| 修改构建与发布校验 | `.agents/skills/verifying/scripts/verify/`、`.github/workflows/` | `verifying` |

## 项目地图

```text
chengzhao-dev/
├── index.qmd                 # README 的 Quarto 入口
├── content/                  # 页面源片段
├── README.md                 # Quarto 生成的 GitHub 页面
├── assets/source/            # 横幅原始素材
├── assets/banner/            # README 直接引用的横幅成品
├── _templates/               # Quarto 正式输出模板
├── config.toml                # 可跨机器共享的工具配置
├── .agents/                  # 技能（含 scripts）、知识、记忆、注册表
└── .github/workflows/        # README 校验与动态资源发布
```

## 两条主流程

### 静态 README

修改 `index.qmd` 或 `content/` → 执行 Quarto 渲染 → 检查 `README.md` → 运行结构、发布面、注册表和媒体校验。`README.md` 不能手工编辑；页面源文件中的 emoji 只用于生成最终 README 的展示内容。

### 动态 SVG

`.github/workflows/snake.yml` 生成浅色/深色贡献图，`.agents/skills/designing-visuals/scripts/activity/add_labels.py` 添加月份和星期标注，`.agents/skills/designing-visuals/scripts/stats/gen_stats.py` 生成浅色/深色统计卡与语言卡，最后将六个 SVG 发布到 `output` 分支。`main` 只保存远程引用，不保存动态 SVG。

## 按需深入阅读

- 硬性规则与执行边界：[`AGENTS.md`](AGENTS.md)。
- `.agents/` 工作区如何分类：[`.agents/README.md`](.agents/README.md)。
- README 渲染与维护：[`maintaining-readme`](.agents/skills/maintaining-readme/SKILL.md)。
- 构建、校验与验收：[`verifying`](.agents/skills/verifying/SKILL.md)。
- 入口文档与资源归类：[`governing-agents`](.agents/skills/governing-agents/SKILL.md)。
- GitHub 发布面的稳定事实：[`publish-governance.md`](.agents/knowledge/repo-layout/publish-governance.md)。
