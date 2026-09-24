---
name: registry-benchmark
description: 注册表检索效果评测结论与生成物位置决策：速查表 + search 粗筛显著优于盲读全文，生成物留在 .agents/ 根。
metadata:
  short-description: 注册检索效果评测与位置决策
  summary: 检索效果评测结论（token/命中/耗时）与生成物保持 .agents/ 根的决策记录
  triggers:
    - 注册表
    - registry
    - 检索效果
    - benchmark
    - token
    - 命中率
    - lookup
    - 生成物位置
---

# 注册表检索效果评测与位置决策

## 评测结论（2026-09-23，工具 `.agents/skills/governing-agents/scripts/registry_bench.py`，报告写 `temp/`）

- QUICK-REFERENCE.md 约 1252 tokens，18 个条目正文合计约 18930 tokens，条目均值约 1052 tokens。
- 典型流程（速查表 + 命中 1 个条目）约 2304 tokens，相对盲读全部正文省约 88%。
- 固定查询集（10 正例 + 3 反例）：any 命中 10/10，反例全部正确返回无结果；`色板` 一类词 top-1 命中 skill 条目属预期（排序在 knowledge 前）。
- search 从全量重扫（约 32 ms）改为读 registry.json（约 0.2 ms），粗筛成本可忽略。

## 生成物位置决策

`registry.json` 与 `QUICK-REFERENCE.md` 保持放在 `.agents/` 根，与 skills/knowledge/memory 平级：
它们是给 agent 阅读的检索入口与数据，不是工具代码，放 `.agents/skills/governing-agents/scripts/` 会混淆职责。

## 维护约定

- 调整 `registry.py` 的 search/lookup 输出或条目元数据后，复跑 benchmark 对比前后指标。
- benchmark 的 token 估算为启发式（CJK 约 1 token/字、ASCII 约 4 字符/token），只看量级不看绝对值。
