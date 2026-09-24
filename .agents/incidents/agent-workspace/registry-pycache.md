---
name: registry-pycache
description: 事故复盘：CI 注册表零漂移检查失败，根因是本地被 gitignore 的产物（__pycache__、tool-cache）被计入技能文件数，registry.json 固化了脏数据。
metadata:
  short-description: 注册表本机产物漂移事故
  summary: CI 零漂移失败而本地通过的根因与修复：技能文件数只统计 git 跟踪文件
  triggers:
    - pycache
    - pyc
    - tool-cache
    - 注册表
    - 零漂移
    - 文件数
    - CI 校验失败
    - registry
    - drift
---

# 注册表文件统计混入本机产物导致 CI 零漂移失败

- 日期：2026-09-23（2026-09-24 复现同类问题后泛化根因）
- 关键词：pycache、pyc、tool-cache、零漂移、文件数、registry、worktree 复现

## 症状

首次 push 后 GitHub Actions 的「校验 README 生成结果」workflow 在「agent 注册表零漂移」一步失败，而同一份代码在本地执行 `registry.py check` 通过。失败信息为「漂移：条目元数据过期 .agents/skills/maintaining-readme/SKILL.md（重跑 build）」。

## 根因

`registry.py` 统计技能文件数时用 `skill_dir.rglob("*")`，把本机运行产生的 gitignore 产物也算了进去：最早是 `scripts/__pycache__/` 里的 `.pyc` 缓存，后来是 `scripts/media/tool-cache/` 下的 FFmpeg 下载包。本地把脏文件数固化进 `registry.json`，CI 干净检出没有这些文件，重新扫描结果与固化的 registry.json 不一致，零漂移检查报「条目元数据过期」。

两次现象完全同型：`designing-visuals` 本地 11 个文件、CI 只有 7 个（多出的 4 个全在 `tool-cache/`）。

## 修复方案

技能 `files` 只统计该目录下 **git 跟踪** 的文件，不再靠手工排除某个缓存目录名——否则换一个 gitignore 产物（tool-cache、构建产物等）就会再次打穿。实现走 `git ls-files`：

```python
def _tracked_files_under(directory: Path) -> set[str]:
    prefix = directory.relative_to(ROOT).as_posix().rstrip("/") + "/"
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", prefix],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        return set()
    return {p for p in result.stdout.split("\0") if p.startswith(prefix)}
```

改动后重跑 `registry.py build` 重建 `registry.json`（`designing-visuals` 的 files 由 11 修正为 7）。

## 验证方法

1. 本地用 `git worktree add --detach temp/ci-repro origin/main` 检出远端树，在其中跑 `registry.py check` 复现失败，修复后同一环境 exit 0。
2. 推送修复 commit 后，通过 GitHub API 确认「校验 README 生成结果」与「刷新个人主页动态资源」两条 workflow 均成功。

## 排查信号

遇到「本地校验通过、CI 同一步骤失败」时，优先怀疑本地环境与 CI 干净检出的差异（缓存文件、本机生成物、未跟踪文件）；用 worktree 检出 origin/main 在本地复现 CI 视角，是最快的定位手段。任何「统计目录文件数」的脚本都必须以 git 跟踪集为准，不能遍历工作树。
