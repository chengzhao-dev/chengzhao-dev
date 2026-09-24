---
name: plan-doc-location
description: 会话计划/审计文档的存放位置规则与根目录白名单校验
metadata:
  summary: 计划/审计文档放 .agents/plan/，根目录白名单由 check_naming.py 拦截
  triggers:
    - 计划文档
    - 审计报告
    - 根目录
    - temp
    - 白名单
---

# 计划与审计文档的存放位置

2026-09-23 起的规则：agent 生成的计划、审计与批次报告放 `.agents/plan/`（受控、随仓库提交）；一次性草稿放根目录 `temp/`（不入库）；根目录不得出现其他 agent 产物。

背景：`REFACTOR-PLAN.md` 与 `REFACTOR-AUDIT.md` 曾由会话直接写在根目录，当时治理规则没有「计划文档」这一类，校验层也无一拦截。用户定调：这类文件不属于仓库公开面，且要跨 IDE 兼容可回退，落 `.agents/plan/`。

落地方式：

- `check_naming.py` 的 `ROOT_ALLOWLIST` 对根目录做封闭白名单，白名单外即失败；新增常驻项须先更新 `structure.md` 2.4 与白名单。
- `registry.py audit` 豁免 `.agents/plan/` 的孤儿检查（由 ARCHITECTURE 等入口指针引用，不挂注册表）。
- 篇幅预算表含 `.agents/plan/*.md` 行（300 行 / 3200 token），`check_budgets.py` 的 `resolve()` 有对应分支；目录暂空是合法状态，该规则此时静默跳过。
- 目录为空时 git 不保留空目录，`.agents/plan/` 消失是正常现象，下次写入计划文档时重建即可。

关联：`[[registry-benchmark]]`（生成物位置）、`[[progressive-nav]]`。
