""".agents/skills/designing-visuals/scripts/media/ 下脚本共用的本机工具解析逻辑。

路径来源按优先级从高到低：

1. 命令行显式传入（``--ffmpeg`` / ``--ffprobe``）
2. 环境变量 ``FFMPEG`` / ``FFPROBE``
3. 仓库根目录 ``config.toml``（项目配置，随仓库提交）
4. ``<tool_cache_dir>/ffmpeg/<版本>/bin/``（bootstrap 脚本下载的静态构建）
5. 系统 PATH

配置文件不存在时直接跳过第 3 步，脚本仍然可用，因此仓库本身不依赖任何本机路径。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
CONFIG_NAME = "config.toml"
DEFAULT_CACHE_DIR = ".agents/skills/designing-visuals/scripts/media/tool-cache"


def load_config(repo: Path = REPO) -> dict:
    """读取仓库根目录的项目配置；文件缺失或损坏时返回空配置而不是报错。"""
    path = repo / CONFIG_NAME
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"警告：{path} 无法解析（{exc}），已忽略该配置", file=sys.stderr)
        return {}


def cache_dir(cfg: dict, repo: Path = REPO) -> Path:
    """工具缓存目录：优先取配置里的 tool_cache_dir，缺省用仓库内的默认位置。"""
    raw = str(cfg.get("tool_cache_dir") or DEFAULT_CACHE_DIR)
    path = Path(raw)
    return path if path.is_absolute() else repo / path


def local_python(cfg: dict) -> str | None:
    """本机配置里的 Python 解释器；未配置或文件不存在时返回 None。"""
    raw = str(cfg.get("python") or "").strip()
    if not raw:
        return None
    path = Path(raw)
    return str(path) if path.is_file() else None


def _cache_candidates(name: str, cfg: dict, repo: Path) -> list[Path]:
    """工具缓存下所有版本 bin/ 里的候选可执行文件，新版本优先。"""
    root = cache_dir(cfg, repo) / "ffmpeg"
    if not root.is_dir():
        return []
    found: list[Path] = []
    for version in sorted(root.iterdir(), reverse=True):
        exe = version / "bin" / f"{name}.exe"
        plain = version / "bin" / name
        for candidate in (exe, plain):
            if candidate.is_file():
                found.append(candidate)
    return found


def find_tool(name: str, explicit: str | None = None, cfg: dict | None = None,
              repo: Path = REPO) -> str | None:
    """按优先级解析 ffmpeg / ffprobe，返回可执行文件路径或 None。"""
    cfg = load_config(repo) if cfg is None else cfg

    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise SystemExit(f"指定的 {name} 不存在：{explicit}")
        return str(path)

    env = os.environ.get(name.upper())
    if env and Path(env).is_file():
        return env

    configured = str(cfg.get(name) or "").strip()
    if configured and Path(configured).is_file():
        return configured

    for candidate in _cache_candidates(name, cfg, repo):
        return str(candidate)

    return shutil.which(name)


def describe_missing(name: str, repo: Path = REPO) -> str:
    """缺少工具时给出的可执行修复提示。"""
    return (
        f"找不到 {name}。请任选一种方式提供：\n"
        f"  1. python .agents/skills/designing-visuals/scripts/media/bootstrap_media.py     # 下载固定版本的 FFmpeg/FFprobe\n"
        f"  2. 在仓库根目录 {CONFIG_NAME} 里填写 {name} 的绝对路径\n"
        f"  3. 设置环境变量 {name.upper()}\n"
        f"  4. 把 {name} 加入系统 PATH"
    )


def webp_info(path: Path) -> dict:
    """直接解析 WebP 容器，读出动画标志、画布尺寸、帧数与总时长。

    Pillow 能解码 WebP，却不暴露逐帧时长（``info`` 里只有 loop 和 background），
    所以时长必须从 ANMF 分块里读，否则校验只能看到 0 秒。
    """
    data = path.read_bytes()
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError(f"{path} 不是 WebP 容器")

    info = {"animated": False, "width": 0, "height": 0,
            "frames": 0, "seconds": 0.0, "loop": None}
    offset = 12
    while offset + 8 <= len(data):
        fourcc = data[offset:offset + 4]
        size = int.from_bytes(data[offset + 4:offset + 8], "little")
        body = data[offset + 8:offset + 8 + size]
        if fourcc == b"VP8X" and len(body) >= 10:
            info["animated"] = bool(body[0] & 0x02)
            info["width"] = int.from_bytes(body[4:7], "little") + 1
            info["height"] = int.from_bytes(body[7:10], "little") + 1
        elif fourcc == b"ANIM" and len(body) >= 6:
            info["loop"] = int.from_bytes(body[4:6], "little")
        elif fourcc == b"ANMF" and len(body) >= 16:
            info["frames"] += 1
            info["seconds"] += int.from_bytes(body[12:15], "little") / 1000
        elif fourcc in (b"VP8 ", b"VP8L") and not info["width"]:
            # 静态 WebP 没有 VP8X，尺寸只能从位流头里取。
            if fourcc == b"VP8 " and len(body) >= 10:
                info["width"] = int.from_bytes(body[6:8], "little") & 0x3FFF
                info["height"] = int.from_bytes(body[8:10], "little") & 0x3FFF
        offset += 8 + size + (size & 1)   # RIFF 分块按偶数字节对齐
    return info


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    """执行外部命令并返回结果；失败时打印 stderr 便于定位。"""
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    if check and result.returncode != 0:
        print("命令失败：" + " ".join(cmd), file=sys.stderr)
        print(result.stderr.strip()[-4000:], file=sys.stderr)
        raise SystemExit(result.returncode)
    return result