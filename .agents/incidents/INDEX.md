# 事故索引

排查失败或行为异常时先查本表，命中相似症状再读取对应案例；其他任务把本目录当作不存在，不读取。与 `memory` 的边界：一般踩坑经验进 `memory`，需要「平时不可见、排查时才检索」的事故复盘进本目录。

条目按领域分组、组内按症状关键词排序；每条两行：关键词行 + 指针行。新增案例后必须在本表补指针，`registry.py audit` 会校验双向一致。

## Agent 工作区

- 关键词：pycache、pyc、tool-cache、注册表、零漂移、文件数、CI 校验失败、registry、drift
- 案例：[agent-workspace/registry-pycache.md](agent-workspace/registry-pycache.md)
- 关键词：轮询、卡住、空转、CI 等待、workflow 轮询、PATH 丢失、grep 判断、推送重试、停止条件
- 案例：[agent-workspace/ci-poll-loop-stuck.md](agent-workspace/ci-poll-loop-stuck.md)

## Git 与 GitHub

- 关键词：cursoragent、Cursor Agent、Contributors、Co-authored-by、attribution、force-push、悬空提交、贡献者
- 案例：[git-github/cursor-contributors.md](git-github/cursor-contributors.md)
