#!/usr/bin/env python3
"""下载固定版本的 FFmpeg/FFprobe 静态构建，供本机生成横幅媒体使用。

只把可执行文件解压到 ``<tool_cache_dir>/ffmpeg/<版本>/bin/``，该目录已被 .gitignore
忽略，不进入版本库；仓库里只保留这份可复现的下载脚本和校验信息。
缓存目录由仓库根目录的 ``config.toml`` 决定，默认是 ``.agents/skills/designing-visuals/scripts/media/tool-cache``。

用法：

    python .agents/skills/designing-visuals/scripts/media/bootstrap_media.py            # 下载并安装
    python .agents/skills/designing-visuals/scripts/media/bootstrap_media.py --check    # 只校验已安装的版本
    python .agents/skills/designing-visuals/scripts/media/bootstrap_media.py --force    # 忽略缓存重新下载
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toolchain  # noqa: E402

# 固定版本、固定下载地址与固定校验和。升级时同时更新这三项，并重跑 --check。
VERSION = "9.0.2"
BUILD = "essentials"
URL = f"https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-{VERSION}-{BUILD}_build.zip"
SHA256 = "60f467265b1e312373dbcd92200c2618a74850f98d3d078e94296bb3fa2047ba"
SOURCE_PAGE = "https://www.gyan.dev/ffmpeg/builds/"

# 静态构建包含 GPL 组件（libx264 等），以 GPL 发布；这里只在本机生成媒体，不再分发。
LICENSE_NOTE = "GPL（含 GPL 组件），来源 gyan.dev，仅在本机生成媒体使用"

BINARIES = ("ffmpeg", "ffprobe")
CHUNK = 1 << 20


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def _download_once(url: str, dest: Path) -> None:
    """下载一次并写入临时文件；连接中途断开时抛错，不留下截断的成品。"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=60) as resp:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        with partial.open("wb") as fh:
            while True:
                block = resp.read(CHUNK)
                if not block:
                    break
                fh.write(block)
                done += len(block)
                if total:
                    pct = done * 100 // total
                    print(f"\r下载中 {pct:3d}%  {done >> 20}/{total >> 20} MiB", end="")
    print()
    # 服务器提前断开时 read() 会正常返回空串，必须显式核对长度，
    # 否则会把截断的文件当成下载成功，后面只能靠 SHA-256 报错。
    if total and done != total:
        raise OSError(f"下载不完整：收到 {done} 字节，期望 {total} 字节")
    partial.replace(dest)


def _download(url: str, dest: Path, attempts: int = 4) -> None:
    """重试下载；每次失败都从头开始，避免把半截数据当成成品。"""
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            _download_once(url, dest)
            return
        except (OSError, urllib.error.URLError) as exc:
            last = exc
            print(f"第 {attempt}/{attempts} 次下载失败：{exc}", file=sys.stderr)
    raise SystemExit(f"下载 {url} 失败：{last}")


def _extract(zip_path: Path, target: Path) -> list[Path]:
    """只取出 bin/ 下的 ffmpeg 与 ffprobe，其余内容不入库也不留盘。"""
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.namelist():
            name = Path(member).name
            if Path(member).parent.name != "bin":
                continue
            stem = Path(name).stem
            if stem not in BINARIES:
                continue
            out = target / name
            with zf.open(member) as src, out.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            written.append(out)
    return written


def _install_dir(cfg: dict) -> Path:
    return toolchain.cache_dir(cfg) / "ffmpeg" / VERSION / "bin"


def _installed(cfg: dict) -> dict[str, Path]:
    target = _install_dir(cfg)
    return {name: target / f"{name}.exe" for name in BINARIES}


def verify(cfg: dict) -> list[str]:
    """校验已安装的工具存在且可执行，返回问题列表。"""
    fails: list[str] = []
    for name, path in _installed(cfg).items():
        if not path.is_file() or path.stat().st_size == 0:
            fails.append(f"缺少 {path}")
            continue
        result = toolchain.run([str(path), "-version"], check=False)
        if result.returncode != 0:
            fails.append(f"{path} 无法运行：{result.stderr.strip()[:200]}")
    return fails


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="下载固定版本的 FFmpeg/FFprobe 静态构建")
    parser.add_argument("--check", action="store_true", help="只校验已安装的工具，不下载")
    parser.add_argument("--force", action="store_true", help="忽略已安装结果，重新下载")
    args = parser.parse_args(argv)

    cfg = toolchain.load_config()
    target = _install_dir(cfg)
    manifest = target.parent / "manifest.json"

    if args.check:
        fails = verify(cfg)
        for msg in fails:
            print(f"::error::{msg}")
        if fails:
            return 1
        print(f"FFmpeg/FFprobe {VERSION} 正常：{target}")
        return 0

    if not args.force and not verify(cfg):
        print(f"已安装 FFmpeg/FFprobe {VERSION}：{target}")
        print("如需重新下载请加 --force")
        return 0

    cache = toolchain.cache_dir(cfg) / "_downloads" / Path(URL).name
    if args.force or not cache.is_file() or _sha256(cache) != SHA256:
        print(f"从 {URL} 下载 {BUILD} 构建…")
        _download(URL, cache)

    actual = _sha256(cache)
    if actual != SHA256:
        print(f"::error::{cache.name} 的 SHA-256 不匹配", file=sys.stderr)
        print(f"  期望 {SHA256}\n  实际 {actual}", file=sys.stderr)
        return 1
    print(f"SHA-256 校验通过：{actual}")

    written = _extract(cache, target)
    missing = [n for n in BINARIES if not (target / f"{n}.exe").is_file()]
    if missing:
        print(f"::error::压缩包中缺少 {missing}", file=sys.stderr)
        return 1

    manifest.write_text(json.dumps({
        "version": VERSION,
        "build": BUILD,
        "url": URL,
        "sha256": SHA256,
        "source_page": SOURCE_PAGE,
        "license": LICENSE_NOTE,
        "binaries": sorted(p.name for p in written),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fails = verify(cfg)
    if fails:
        for msg in fails:
            print(f"::error::{msg}")
        return 1
    print(f"已安装 FFmpeg/FFprobe {VERSION}：{target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())