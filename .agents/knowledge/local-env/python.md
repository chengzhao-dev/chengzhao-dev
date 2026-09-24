---
name: local-python
description: 本机 Python 解释器的位置与统一用法：以 config.toml 的 python 字段为唯一事实源，脚本与注册表工具均用它运行。
metadata:
  short-description: 本机 Python 解释器事实
  summary: 本机 Python 解释器位置与统一用法，唯一事实源是 config.toml 的 python 字段
  triggers:
    - python
    - 解释器
    - miniforge
    - conda
    - 环境
    - Store 占位
    - 本机工具
    - shebang
---

# 本机 Python 解释器

本仓库脚本的解释器以根目录 `config.toml` 的 `python` 字段为唯一事实源；本文只记录本机现状与排查方法，不重复定义查找逻辑。

## 本机现状

- 解释器：`D:/ProgramData/miniforge3/python.exe`（miniforge3 自带，非系统安装）
- 版本：Python 3.14；`PATH` 上的 `python`/`python3` 是 Microsoft Store 占位程序，**不可用**
- `py` 启动器、pip 独立入口同样不存在；一切脚本调用都走 `config.toml` 里的绝对路径

## Shebang 与调用分工

- 可执行脚本首行保留 `#!/usr/bin/env python3`（Python 官方推荐的跨 Unix/Windows 可移植写法；规范见 `writing-chinese` 的 `references/comment-format.md`）
- 用显式解释器调用时 shebang 只是注释，无害；本机仍应执行：`D:/ProgramData/miniforge3/python.exe .agents/skills/verifying/scripts/verify/run_all.py`（路径以 `config.toml` 为准）
- 不依赖直接执行脚本文件或 PATH 上的 `python3`，避免命中 Store 占位

## 维护约定

- 换机器或升级 miniforge3 时，只改 `config.toml` 的 `python` 字段，本文同步更新版本号
- `PATH` 上出现真实解释器时，可把 `config.toml` 的 `python` 改回留空，本文同步删除本机路径
- 新写脚本时不做额外解释器探测，统一假设调用方已按 `config.toml` 选好解释器
