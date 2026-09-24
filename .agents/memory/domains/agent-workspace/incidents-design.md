---
name: incidents-design
description: 设计决策：事故案例库放 .agents/incidents/ 而非 memory，检索统一采用 MD+frontmatter 单一事实源 + 分层 MD 索引。
metadata:
  short-description: incidents 目录设计决策
  summary: incidents 与 memory 的边界、平时不可见的豁免机制、检索方案选型理由
  triggers:
    - incidents
    - 事故
    - 案例库
    - 错误案例
    - 检索方案
    - 索引
---

# incidents 事故案例库的设计决策

- 日期：2026-09-23
- 关键词：incidents、事故复盘、案例库、检索方案、平时不可见、INDEX.md

## 决策内容

1. 事故案例放 `.agents/incidents/<领域>/<主题>.md`，不放 `memory`：两者内容形态相同（现象 → 根因 → 对策），差异在**读取时机**——memory 索引每次会话都读，incidents 要求平时任务当不存在，只在排查失败时按症状检索。放 memory 会让案例常驻每次会话，违背设计目标。
2. 平时不可见由结构保证，不靠 agent 自觉：整个 `incidents/`（含 `INDEX.md`）在 `registry.py` 孤儿检查中豁免（与 `.agents/plan/` 同待遇），不进 `registry.json`、不进 `QUICK-REFERENCE.md`；唯一入口是 `AGENTS.md` 任务起点的一条条件指令。
3. 检索方案统一为：MD+frontmatter 是唯一事实源，JSON 只是 build 期机器产物（`registry.json` 已是此模式）。agent 的检索面是紧凑 MD 索引（`incidents/INDEX.md`，每案例 2 行），机器检索面是 JSON/CLI。不用 JSON 做案例主格式：braces 与引号使同信息多耗 2-3 倍 token，且人不可维护。
4. 规模化路径：N ≤ 约 50 时单张 INDEX.md 够用；超过后 INDEX.md 退化为域路由、各域加 `index.md`，与 memory 的三层结构完全同构。
5. 一致性由脚本保证：audit 把 incidents 加入死指针扫描根，并校验 INDEX↔案例双向一致（案例漏登记、INDEX 指向不存在文件都会报错）。

## 排查信号

- 若有人提议把事故案例写进 memory 或 registry.json，先确认其是否需要「平时不可见」；需要则走 incidents。
- 若 audit 报「事故索引」类错误，说明 INDEX.md 与案例文件不同步，按报错补登记或删死指针。
- 外部参考：agents.md 与 GitHub 官方规范无错误案例库机制，此设计为自创约定；Claude Code 生态（lessons-md 的 Related 字段、Anthropic just-in-time 索引论述）提供了模式依据。
