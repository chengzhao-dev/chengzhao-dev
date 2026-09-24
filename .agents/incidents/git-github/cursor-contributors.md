---
name: cursor-contributors
description: 事故复盘：Cursor Attribution 自动注入 Co-authored-by，导致 GitHub Contributors 出现 cursoragent；改写历史强推后悬空提交仍可按 SHA 访问，删库重建或 Support 清除。
metadata:
  short-description: Cursor 共著污染 Contributors 事故
  summary: Cursor 注入共著 trailer 污染 Contributors 的完整复盘：历史改写、强推、悬空对象与删库重建 / Support 清除
  triggers:
    - cursoragent
    - Cursor Agent
    - Contributors
    - Co-authored-by
    - attribution
    - force-push
    - 悬空提交
    - 贡献者
---

# Cursor 共著注入污染 GitHub Contributors

- 日期：2026-09-24
- 关键词：cursoragent、Contributors、Co-authored-by、attribution、force-with-lease、悬空提交、GitHub Support

## 症状

仓库 Contributors 页出现 `cursoragent`（Cursor Agent）并持有贡献徽章，而实际提交者只有本人。检查历史发现推送的 HEAD 提交 [`fed6192`](https://github.com/chengzhao-dev/chengzhao-dev/commit/fed61926eebdc4c9f616034fc3a8f72cce9fc102) 信息末尾被追加了共著 trailer：

```text
Co-authored-by: Cursor <cursoragent@cursor.com>
```

## 根因

Cursor 的 IDE 与 CLI 默认开启 Attribution，提交时自动注入共著 trailer。本机还有一层包装：环境变量 `CURSOR_AGENT=1` 时，任何形如 `git commit` 的命令都会被改写为追加 `--trailer "Co-authored-by: Cursor <cursoragent@cursor.com>"`，连 `git commit --amend` 也逃不掉，导致第一次重写历史（`reset --soft` 后重新提交）仍然带毒。

GitHub 把 `cursoragent@cursor.com` 识别为 `cursoragent` 用户，按共著计入 Contributors 并授予徽章。Cursor Settings → Agent → Attribution 的开关只影响后续提交，不会清理已推送历史。

## 修复过程

1. **改写可达历史**：`git commit` 的包装无法绕过，改用底层 plumbing——用 `git commit-tree` 以原 tree、原作者与时间、无 trailer 的信息直接构建提交对象，再把 `main` 指过去，得到干净的 `1c63219`。
2. **强推**：确认仓库无分支保护 ruleset 后，`git push --force-with-lease origin main` 覆盖远端。
3. **固化预防**：`AGENTS.md` 增加归属禁令；新增 `.agents/skills/verifying/scripts/verify/check_commit_attribution.py` 静态校验并接入 CI；memory 记 `cursor-attribution` 条目。
4. **发现残留**：强推后按 SHA 访问 `fed6192` 仍能打开——它是脱离分支的悬空对象，GitHub 不会立刻 GC；本机 reflog 也还持有 `fed6192`、`0de4a18`、`14a711a` 等污染对象。

## 剩余残留的清理

本机对象用 reflog 过期加 gc 清除（不改远程引用）：

```powershell
git reflog expire --expire=now --all
git gc --prune=now
```

GitHub 侧的悬空提交，仓库所有者无法用普通 `git push` 删除。主路径是**删除并重建仓库**：`DELETE /repos/<owner>/<repo>` 后以同名重建空仓，再推干净历史；旧 SHA 随旧仓库一并作废，不需要等 GitHub GC。本仓是空壳 Profile 仓，重建只丢 CI 运行历史，可接受。

备选路径（不便删库时）：向 GitHub Support 申请清除不可达对象。工单正文（提交入口：<https://support.github.com/contact>，选「Remove cached or sensitive commit data」类请求）：

```text
Subject: Request to purge unreachable commit data from chengzhao-dev/chengzhao-dev

Hi GitHub Support,

I rewrote the default branch of my repository chengzhao-dev/chengzhao-dev
and force-pushed, so the commit below is no longer reachable from any
branch or tag. However, it is still accessible by SHA:

  https://github.com/chengzhao-dev/chengzhao-dev/commit/fed61926eebdc4c9f616034fc3a8f72cce9fc102

Its message ends with an unintended attribution trailer:

  Co-authored-by: Cursor <cursoragent@cursor.com>

This made "cursoragent" appear under the repository Contributors.
Could you please run a garbage collection on the repository and remove
this unreachable commit object (and any sibling rewritten commits from
the same push, if still stored)?

The current default branch (main @ 1c632191) is clean and contains no
Cursor attribution. Thank you!
```

工单需要本人在已登录的 GitHub 账号下提交发送；Support 处理完成后旧 SHA 链接才会上 404。

## 验证方法

1. 本机：`git cat-file -t fed61926eebdc4c9f616034fc3a8f72cce9fc102` 报 not a valid object；`check_commit_attribution.py` 输出 PASS。
2. 远端：Contributors API（`repos/chengzhao-dev/chengzhao-dev/contributors`）只返回 `chengzhao-dev`；Contributors 图页无 cursoragent（图页数据有缓存，刷新有延迟）。
3. 旧 SHA 链接在删库重建（或 Support 处理）后返回 404。
4. Cursor Settings → Agent → Attribution 保持关闭，防止再次注入。

## 排查信号

- Contributors 出现 `cursoragent` / Cursor Agent：先 `git log --all --grep=cursoragent -i` 定位污染提交。
- force-push 之后旧 SHA 仍能打开属正常现象：那是悬空对象，本机用 reflog expire + gc 清理；远端走删库重建（主路径）或 GitHub Support（备选），不要试图再次改写历史。
- `git commit` 怎么改信息都带 trailer：怀疑 Attribution 包装，改用 `git commit-tree` 等 plumbing 绕过。
