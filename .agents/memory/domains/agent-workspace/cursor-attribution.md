---
name: cursor-attribution
description: 经验教训：Cursor 会自动给提交追加 Co-authored-by 归属，导致 GitHub Contributors 出现 cursoragent，本仓一律去除。
metadata:
  short-description: Cursor 提交归属会污染 Contributors
  summary: Cursor 自动注入的共著 trailer 会让 cursoragent 出现在 Contributors，去除与预防方法
  triggers:
    - Cursor
    - cursoragent
    - Contributors
    - Co-authored-by
    - attribution
    - 共著
    - 提交信息
    - 归属
---

# Cursor 提交归属污染 GitHub Contributors

- 日期：2026-09-24
- 关键词：Cursor、cursoragent、Contributors、Co-authored-by、attribution、force-with-lease

## 现象与根因

Cursor 的 IDE 与 CLI 默认开启 Attribution，会在提交信息里注入 `Co-authored-by: Cursor <cursoragent@cursor.com>`；本机包装甚至在 `CURSOR_AGENT=1` 时改写一切 `git commit` 类命令。GitHub 把该邮箱识别为 `cursoragent` 用户，计入 Contributors 并授予贡献徽章。

## 对策

1. 本机关闭 Cursor Settings → Agent → Attribution，从源头不再注入。
2. 提交前检查：提交信息不得含 `cursoragent@cursor.com`、`Co-authored-by: Cursor`，也不得把 Cursor 写成 author/committer。仓库侧由 `.agents/skills/verifying/scripts/verify/check_commit_attribution.py` 静态拦截，已接入 `run_all.py` 与 CI。
3. 已推送的归属只能改写历史后 `git push --force-with-lease origin main`；注意包装绕不开时用 `git commit-tree` 重建提交。
4. 排查 Contributors 污染的完整事故复盘（改写过程、悬空对象、Support 清除工单）见 incidents 案例 `git-github/cursor-contributors`，不要把整场复盘堆在 memory。
