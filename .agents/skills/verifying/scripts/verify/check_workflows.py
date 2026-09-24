#!/usr/bin/env python3
"""校验工作流与仓库配置的静态约束。

用法：
  python .agents/skills/verifying/scripts/verify/check_workflows.py

检查项：YAML/TOML 可解析；工作流的权限与并发声明；工作流引用的本地脚本存在；
忽略规则覆盖缓存、临时目录与密钥文件，且这些路径没有被跟踪的文件。
只做本地静态解析，不做网络探测。需要 PyYAML。
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]

# 每个工作流的权限下限：README 校验只读仓库，动态资源发布需要写 output 分支。
EXPECTED_PERMISSIONS = {
    "readme.yml": {"contents": "read"},
    "snake.yml": {"contents": "write"},
}
# snake.yml 的贪吃蛇与统计卡发布共用一个并发组，防止两次发布互相覆盖。
NEEDS_CONCURRENCY = {"snake.yml"}
REQUIRED_IGNORE_PATTERNS = (
    "__pycache__/",
    ".agents/skills/designing-visuals/scripts/media/tool-cache/",
    "/temp/",
    ".env",
    "*.pem",
    "*.key",
)
IGNORED_TRACKED_PATTERNS = (
    "*__pycache__*",
    ".agents/skills/designing-visuals/scripts/media/tool-cache/*",
    "temp/*",
    "*.env",
    "*.pem",
    "*.key",
    "*.html",
    "*_files/*",
    ".quarto/*",
)
# 允许工具配置路径如解释器位置；用户主目录等可识别个人的位置仍禁止。
USER_PROFILE_PATH = re.compile(r"(?i)[A-Z]:[\\/]Users[\\/][^\s\"']+")


def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8",
    )
    return result.stdout.splitlines()


def check_workflows(findings: list[str]) -> None:
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        name = path.name
        text = path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            findings.append(f"{name}：YAML 无法解析（{exc}）")
            continue
        # YAML 1.1 会把裸的 on 键解析成布尔 True，两种键名都接受。
        triggers = data.get("on") if isinstance(data, dict) else None
        if triggers is None and isinstance(data, dict):
            triggers = data.get(True)
        if not isinstance(data, dict) or not triggers or not data.get("jobs"):
            findings.append(f"{name}：缺少 on 触发器或 jobs 定义")

        expected = EXPECTED_PERMISSIONS.get(name)
        if expected is not None and data.get("permissions") != expected:
            findings.append(f"{name}：permissions 为 {data.get('permissions')}，期望 {expected}")
        if name in NEEDS_CONCURRENCY and not data.get("concurrency"):
            findings.append(f"{name}：缺少 concurrency 并发保护")

        for ref in sorted(set(re.findall(r"\.agents/skills/[\w/-]+/scripts/[\w/.-]+\.py", text))):
            if not (ROOT / ref).is_file():
                findings.append(f"{name}：引用的脚本不存在：{ref}")


def check_quarto_config(findings: list[str]) -> None:
    path = ROOT / "_quarto.yml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        findings.append(f"_quarto.yml：YAML 无法解析（{exc}）")
        return
    if not isinstance(data, dict) or "project" not in data:
        findings.append("_quarto.yml：缺少 project 配置")


def check_tools_config(findings: list[str]) -> None:
    path = ROOT / "config.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        findings.append(f"config.toml：无法解析（{exc}）")
        return
    for key, value in data.items():
        if isinstance(value, str) and USER_PROFILE_PATH.search(value):
            findings.append(f"config.toml：{key} 含可识别个人的用户主目录路径")


def check_ignore_rules(findings: list[str]) -> None:
    lines = [line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()]
    for pattern in REQUIRED_IGNORE_PATTERNS:
        if not any(line == pattern or line.startswith(pattern) for line in lines):
            findings.append(f".gitignore：缺少忽略规则 {pattern}")
    tracked = tracked_paths()
    for path in tracked:
        for pattern in IGNORED_TRACKED_PATTERNS:
            if fnmatch.fnmatch(path, pattern):
                findings.append(f"{path}：命中忽略规则 {pattern}，不应被 Git 跟踪")
                break


def main() -> int:
    findings: list[str] = []
    check_workflows(findings)
    check_quarto_config(findings)
    check_tools_config(findings)
    check_ignore_rules(findings)
    for item in findings:
        print(f"FAIL: {item}")
    print(f"{'PASS' if not findings else 'FAIL'}: {len(findings)} 处问题")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
