---
name: progressive-nav
description: 本轮重构采用双入口、渐进式导航、平衡清理和分阶段迁移的决策记录。
metadata:
  short-description: 文档信息架构决策
  summary: 人类阅读优先、Agent 路由其次的文档重构选择与边界
  triggers:
    - 渐进式导航
    - 双入口
    - 文档重构
    - 平衡清理
    - 信息架构
---

# 文档信息架构决策

## 决策

- `ARCHITECTURE.md` 服务新人和人类读者，解释项目地图与主流程。
- `AGENTS.md` 服务 Agent，保留硬性约束、隐私红线和最短路由。
- `.agents/README.md` 解释工作区分类，不复制根入口正文。
- 所有 Markdown 按“定位 → 找路 → 地图 → 执行 → 深入”渐进展开，规范见 `governing-agents/references/progressive-nav.md`。
- 冗余采用平衡清理：确认无引用、无调用、无 CI 依赖且无唯一价值后才删除；不确定项先报告。
- 重构按小批次执行，每批先更新唯一事实源，再同步索引和生成物。

## 校验边界

GitHub 发布面采用基础可发布标准：阻断明确敏感内容、生成物漂移、结构错误和缓存污染；外链只做静态检查，不把暂时的网络故障作为合并阻断。

## 来源

决策依据包括 GitHub 的仓库健康文件与 CODEOWNERS 文档、OpenAI Codex 的 `AGENTS.md`、Microsoft Writing Style Guide。稳定事实沉淀在 `knowledge/repo-layout/publish-governance.md`，执行步骤仍由技能负责。
