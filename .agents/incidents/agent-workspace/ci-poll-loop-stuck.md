---
name: ci-poll-loop-stuck
description: 事故复盘：推送成功后 CI 轮询脚本空转 12 分钟，根因是循环退出条件的 grep 判断逻辑永假，外加子 shell 丢失 PATH。
metadata:
  short-description: CI 轮询循环空转事故
  summary: 推送已完成但轮询脚本永不退出：退出条件缺陷与 PATH 丢失两个根因及修复写法
  triggers:
    - 轮询
    - 卡住
    - 空转
    - CI 等待
    - workflow 轮询
    - PATH 丢失
    - grep 判断
---

# CI 轮询脚本空转导致误判推送卡住

- 日期：2026-09-23
- 关键词：轮询、卡住、空转、退出条件、grep、PATH、workflow 轮询

## 症状

git push 已成功（输出 `671d66b..84d2e11 main -> main`），但随后的 CI 状态轮询脚本一直不退出，空转 12 分钟直到被手动取消，让人误以为「推送卡住了」。另有一次附带症状：同一类 Bash 调用里 `python` 报「Python was not found」（Microsoft Store 占位符），而之前的调用一直正常。

同会话内还发生了第二次同类问题：推送遇到网络阻断（`Failed to connect to github.com:443` / `Recv failure: Connection was reset`）后，重试循环写成「每 50 秒一次、成功才停」，没有失败上限，网络持续不通时无限重试，同样只能手动取消。

## 根因

两个独立问题叠加：

1. 轮询循环的退出条件写成 `grep -qv "queued\|in_progress\|pending"` 加 `grep -q "completed"` 再数 `completed` 出现次数凑 2——`grep -v` 作用于整行输出，行里同时含有 completed 状态的 run 名与其他文本，逻辑永远凑不齐，循环永不退出。判断逻辑只在自己拼的字符串组合上「看起来对」，没有对真实 API 输出验证过一次。
2. 新开的 Bash 调用没有重新 `export PATH`（本机裸 `python` 是 Microsoft Store 占位符），curl 结果落地后解析失败。
3. 推送重试循环是同根因的另一个面：退出条件只有「成功」，没有失败上限，网络长时间不通时退化为无限循环。

## 修复方案

1. CI 状态确认不用循环轮询，改一次性查询：`curl` 拉取 `actions/runs?head_sha=<sha>` 落到 `temp/`，用 python 解析后直接读 `status`/`conclusion` 字段；未跑完就隔几分钟再查一次，每次都是独立短命令。
2. 每次 Bash 调用开头都显式 `export PATH="/d/ProgramData/miniforge3:$PATH"`，不依赖上一次调用的环境。
3. 通用规则：任何重试/轮询循环必须有**固定失败上限**——推送重试固定 3-7 次（间隔约 50 秒），连续达到上限仍是 `Failed to connect` / `Connection was reset` 类网络错误就停止并报告，不无限等待；网络何时恢复不可控，由下一次任务再验证。

## 验证方法

对 SHA 84d2e11 用一次性查询确认：`校验 README 生成结果` 与 `刷新个人主页动态资源` 均为 completed/success；同时 `git rev-parse origin/main HEAD` 两侧一致、`git status` 干净，证明推送从未卡住，卡住的只是轮询脚本本身。

## 排查信号

遇到「命令输出显示成功但后续脚本不退出」时，先怀疑退出条件的判断逻辑，把条件对真实输出单测一次再进循环；「昨天的命令今天报 python 不存在」类症状，先查当前调用是否丢了 PATH 导出。「循环只在成功时退出」是反模式——退出条件必须包含失败上限，否则外部依赖持续不可用时循环永不结束。
