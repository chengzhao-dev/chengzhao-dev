#!/usr/bin/env python3
"""GitHub 发布面静态检查。

检查受控文件中的高置信度敏感模式、机器绑定路径和明显无效 URL。
脚本只读文件，不修改 README、资源或注册表；示例变量名与公开固定路径不在扫描范围内。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

TRACKED_EXTENSIONS = {
    ".md",
    ".qmd",
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".lua",
    ".json",
}

PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"]?[A-Za-z0-9+/=_-]{20,}"
)
WINDOWS_USER_PATH = re.compile(r"(?i)[A-Z]:[\\/]Users[\\/][^\s\"']+")
MACHINE_PATH = re.compile(r"(?i)[A-Z]:[\\/]ProgramData[\\/][^\s\"']+")
URL = re.compile(r"https?://[^\s)<>\"']+")
EMOJI = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]")
# 白名单：精确值加原因，不放真实秘密。解释器等纯工具路径经确认不属于隐私。
VALUE_ALLOWLIST = {
    "D:/ProgramData/miniforge3/python.exe": "config.toml 与知识条目记录的本机 Python 解释器，纯工具路径不含密钥",
}
# README 生成物与它的展示内容源（index.qmd、content/、_templates/）允许携带 emoji；
# 其余受控文档、脚本与配置一律不得新增 emoji。
EMOJI_ALLOWED_PREFIXES = (
    "README.md",
    "index.qmd",
    "content/",
    "_templates/",
)
NO_EMOJI_PREFIXES = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    ".agents/plan/",
    ".github/",
    ".agents/skills/",
    "config.toml",
)
# 允许出现的 URL 域名，按用途分组；README 组件白名单另见 check_readme.py
# 与知识条目 trust-tiers.md，这里覆盖的是全仓库受控文本里的链接引用。
ALLOWED_DOMAINS = {
    # GitHub 官方托管与 API
    "github.com",
    "api.github.com",
    "docs.github.com",
    "support.github.com",
    "raw.githubusercontent.com",
    "opengraph.githubassets.com",
    # 本仓库作者的 GitHub Pages 站点
    "chengzhao-dev.github.io",
    # 徽章服务（信任层级第 2 级，见 trust-tiers.md）
    "img.shields.io",
    "shields.io",
    # 技术标准与官方文档（技能与知识条目的参考来源）
    "www.w3.org",
    "docs.python.org",
    "www.lua.org",
    "toml.io",
    "yamllint.readthedocs.io",
    "google.github.io",
    "openstd.samr.gov.cn",
    # FFmpeg Windows 构建下载源（bootstrap_media.py）
    "www.gyan.dev",
    # 已有知识条目引用的公开文档站点
    "learn.microsoft.com",
    "opensource.guide",
    "agents.md",
    "platform.claude.com",
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [ROOT / line for line in result.stdout.splitlines() if Path(line).suffix.lower() in TRACKED_EXTENSIONS]


def check_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{path.relative_to(ROOT)}：不是 UTF-8 文本"]

    failures: list[str] = []
    relative = path.relative_to(ROOT)
    relative_posix = relative.as_posix()
    if EMOJI.search(text) and not relative_posix.startswith(EMOJI_ALLOWED_PREFIXES):
        failures.append(f"{relative}：emoji 只允许出现在 README 生成物与它的展示内容源")
    if relative_posix.startswith(NO_EMOJI_PREFIXES) and EMOJI.search(text):
        failures.append(f"{relative}：受控源文件、脚本或配置不得包含 emoji")
    for line_number, line in enumerate(text.splitlines(), 1):
        if PRIVATE_KEY.search(line):
            failures.append(f"{relative}:{line_number}：发现私钥头")
        if SECRET_ASSIGNMENT.search(line) and "${{" not in line and "example" not in line.lower():
            failures.append(f"{relative}:{line_number}：发现疑似已写入的密钥赋值")
        if (WINDOWS_USER_PATH.search(line) or MACHINE_PATH.search(line)) and not any(
            allowed in line for allowed in VALUE_ALLOWLIST
        ):
            failures.append(f"{relative}:{line_number}：发现机器绑定的绝对路径")

    for match in URL.finditer(text):
        url = match.group(0).rstrip(".,;:！。")
        domain = re.sub(r"^https?://", "", url).split("/", 1)[0].lower().split(":", 1)[0]
        if domain not in ALLOWED_DOMAINS:
            failures.append(f"{relative}：URL 域名不在允许清单：{domain}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查 GitHub 发布面的敏感内容与静态 URL")
    parser.add_argument("--files-from-git", action="store_true", help="扫描 Git 已跟踪及未忽略文件（默认行为）")
    args = parser.parse_args(argv)
    del args

    failures = [failure for path in tracked_files() if path.is_file() for failure in check_file(path)]
    if failures:
        for failure in failures:
            print(f"::error::{failure}")
        return 1
    print("GitHub 发布面静态检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
