---
name: verify-approach
description: 为什么验收放弃浏览器截图、改用静态校验的决策记录与由来；现行流程见 maintaining-readme。
metadata:
  short-description: 验收方式决策记录
  summary: 验收以静态校验为准（无截图）的决策由来，现行清单见技能
  triggers:
    - 验收
    - 截图
    - 静态校验
    - 幂等
    - 决策
---

# 验收方式决策记录

- 日期：2026-09-23
- 关键词：验收、无截图、幂等渲染、无本地模拟

## 决策与由来

- 验收不使用浏览器无头截图与图像比对：截图式验收 token 消耗高、结果不稳定，而页面正确性（结构、编码、引用完整）都能被确定性断言覆盖。
- 现行验收流程与检查清单见 `maintaining-readme` 的「验证清单」；CI 不安装浏览器。
- 规范类断言（`.agents/skills/verifying/scripts/verify/check_budgets.py`、`.agents/skills/verifying/scripts/verify/check_naming.py`、`.agents/skills/governing-agents/scripts/registry.py audit`）只在本地可选运行，不进 GitHub Actions；工具输出一行一条、结论简洁，避免占用过多 token。

## 时点事实

- 2026-09-23 经可行性校验（temp/check_local_actions.py）判定本地模拟 Actions 产物不可行：统计卡需 GITHUB_TOKEN 调 GraphQL，贪吃蛇依赖 Platane/snk action 无法本地复现，本地产物必然陈旧；模拟预览的脚本与流程文档已删除，SVG 效果一律以 `output` 分支线上产物为准。

- `repo-table.lua` 已随推荐项目列表化移除（README 不再用表格）。
- `embed_activity_date.py` 已改名为 `add_labels.py`（职责是叠加月份/星期标注，不再是日期）。
