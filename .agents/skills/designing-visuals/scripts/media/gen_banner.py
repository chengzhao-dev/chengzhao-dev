#!/usr/bin/env python3
"""从源素材生成顶部横幅媒体：assets/banner/pixel-flower-landscape-64color.webp 与
assets/banner/pixel-flower-landscape-64color.png。

``assets/banner/pixel-flower-landscape-64color.webp`` 是动画 WebP，作为首选展示资源；
``assets/banner/pixel-flower-landscape-64color.png`` 是从静态源图减色后的静态降级，
文件名里的 ``-64color`` 表示它被减色到 64 色，作为 GitHub 不稳定支持 WebP 时的可靠回退。
两个文件都由本脚本生成，不要手改。

源素材放在受控目录 assets/source/pixel-flower-landscape/ 下：动画取自 mp4，
静态降级取自同构图的 png。

用法：

    python .agents/skills/designing-visuals/scripts/media/gen_banner.py --source 源视频.mp4   # 生成并校验
    python .agents/skills/designing-visuals/scripts/media/gen_banner.py --check               # 只校验现有资源
    python .agents/skills/designing-visuals/scripts/media/gen_banner.py --ffmpeg ... --ffprobe ...   # 显式指定工具

工具路径的查找顺序见 .agents/skills/designing-visuals/scripts/media/toolchain.py；缺失时可先执行
``python .agents/skills/designing-visuals/scripts/media/bootstrap_media.py``。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toolchain  # noqa: E402
from banner_spec import (  # noqa: E402
    DEFAULT_SECONDS,
    FALLBACK_PATH,
    HEIGHT,
    MAX_FALLBACK_BYTES,
    MAX_SECONDS,
    MAX_WEBP_BYTES,
    MIN_SECONDS,
    PALETTE_COLORS,
    WEBP_PATH,
    WIDTH,
)

REPO = toolchain.REPO
ASSETS = REPO / "assets"
# 横幅规格与上限以 banner_spec.py 为唯一事实源，本脚本只保留编码侧参数。
ASPECT = WIDTH / HEIGHT
SOURCE_DIR = ASSETS / "source" / "pixel-flower-landscape"
DEFAULT_STILL_SOURCE = SOURCE_DIR / "pixel-flower-landscape.png"

# 画面是缓慢流动的水面与花丛，10 fps 已能看出动感，体积又远小于源视频的 24 fps。
FPS = 10

# 质量 55 是实测的平衡点：1280×720 的动画 WebP 约 3 MiB，
# 继续提高质量体积增长很快，而这幅画在 README 显示宽度下已看不出差别。
QUALITY = 55            # libwebp 质量，0-100
COMPRESSION = 6         # libwebp 压缩方法，0-6，越大越慢但越小
LOOP = 0                # 0 表示无限循环

# 无抖动量化：像素画本身是离散色块，抖动会引入噪点，破坏原本的像素质感。
DITHER = Image.Dither.NONE


def probe(ffprobe: str, source: Path) -> dict:
    """读取源视频的尺寸、时长和帧率。"""
    result = toolchain.run([
        ffprobe, "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,duration",
        "-show_entries", "format=duration",
        "-of", "json",
        str(source),
    ])
    data = json.loads(result.stdout)
    streams = data.get("streams") or []
    if not streams:
        raise SystemExit(f"源视频没有视频流：{source}")
    stream = streams[0]

    def _duration() -> float:
        for raw in (stream.get("duration"), (data.get("format") or {}).get("duration")):
            try:
                value = float(raw)
            except (TypeError, ValueError):
                continue
            if value > 0:
                return value
        raise SystemExit(f"无法确定源视频时长：{source}")

    fps_raw = str(stream.get("avg_frame_rate") or "0/1")
    num, _, den = fps_raw.partition("/")
    try:
        src_fps = float(num) / float(den) if float(den) else 0.0
    except ValueError:
        src_fps = 0.0

    return {
        "width": int(stream.get("width") or 0),
        "height": int(stream.get("height") or 0),
        "duration": _duration(),
        "fps": src_fps,
    }


def crop_filter(src_w: int, src_h: int) -> str:
    """按 16:9 居中裁切再缩放到目标尺寸，避免横幅被拉伸变形。"""
    if src_w <= 0 or src_h <= 0:
        return f"scale={WIDTH}:{HEIGHT}:flags=lanczos"
    if src_w / src_h > ASPECT:
        crop_h = src_h
        crop_w = int(round(src_h * ASPECT))
        x, y = (src_w - crop_w) // 2, 0
    else:
        crop_w = src_w
        crop_h = int(round(src_w / ASPECT))
        x, y = 0, (src_h - crop_h) // 2
    crop_w, crop_h = max(2, crop_w - crop_w % 2), max(2, crop_h - crop_h % 2)
    x, y = max(0, x), max(0, y)
    return f"crop={crop_w}:{crop_h}:{x}:{y},scale={WIDTH}:{HEIGHT}:flags=lanczos"


def build_webp(ffmpeg: str, source: Path, filters: str, start: float, seconds: float) -> None:
    toolchain.run([
        ffmpeg, "-y", "-loglevel", "error",
        "-ss", f"{start:.3f}", "-i", str(source),
        "-an",                                   # 横幅不需要音频，也避免动画 WebP 带上音轨
        "-t", f"{seconds:.3f}",
        "-vf", f"{filters},fps={FPS}",
        "-c:v", "libwebp_anim",
        "-lossless", "0",
        "-q:v", str(QUALITY),
        "-compression_level", str(COMPRESSION),
        "-loop", str(LOOP),
        str(WEBP_PATH),
    ])


def quantize(image: Image.Image, colors: int) -> Image.Image:
    """把 RGB 图减色为指定色数的调色板图，不做抖动，保住像素画的离散色块。"""
    return image.quantize(colors=colors, method=Image.MEDIANCUT, dither=DITHER)


def build_still(still_source: Path, colors: int) -> None:
    """从静态源图生成降级 PNG：先缩放到与动画相同的 1280×720 再减色。"""
    with Image.open(still_source) as img:
        rgb = img.convert("RGB")

    scaled = rgb.resize((WIDTH, HEIGHT), Image.LANCZOS)
    quantize(scaled, colors).save(FALLBACK_PATH, "PNG", optimize=True)


def _colors_used(image: Image.Image) -> int:
    """统计图片实际用到的颜色数；调色板图按 RGB 展开后再数。"""
    return len(image.convert("RGB").getcolors(maxcolors=1 << 24) or [])


def verify(colors: int) -> list[str]:
    """校验两个资源可解码、尺寸正确、动画与体积符合预期。"""
    fails: list[str] = []

    if not WEBP_PATH.is_file() or WEBP_PATH.stat().st_size == 0:
        fails.append(f"缺少 {WEBP_PATH.relative_to(REPO)}")
    else:
        size = WEBP_PATH.stat().st_size
        # 容器层校验用自带的 RIFF 解析器，能读到 Pillow 不暴露的逐帧时长。
        try:
            meta = toolchain.webp_info(WEBP_PATH)
            if not meta["animated"]:
                fails.append("横幅动画 WebP 的容器未标记为动画")
            if (meta["width"], meta["height"]) != (WIDTH, HEIGHT):
                fails.append(f"横幅动画 WebP 画布为 {meta['width']}×{meta['height']}，期望 {WIDTH}×{HEIGHT}")
            if meta["frames"] < 2:
                fails.append(f"横幅动画 WebP 只有 {meta['frames']} 帧，不是动画")
            if not (MIN_SECONDS <= meta["seconds"] <= MAX_SECONDS):
                fails.append(f"横幅动画 WebP 时长 {meta['seconds']:.1f}s，超出 {MIN_SECONDS}-{MAX_SECONDS}s 目标区间")
            print(f"{WEBP_PATH.name}：{meta['width']}×{meta['height']}，{meta['frames']} 帧，"
                  f"约 {meta['seconds']:.1f}s，{size >> 10} KiB")
        except ValueError as exc:
            fails.append(str(exc))
        # 再用 Pillow 真正解码一次，确认像素数据没坏。
        try:
            with Image.open(WEBP_PATH) as img:
                img.load()
                if img.size != (WIDTH, HEIGHT):
                    fails.append(f"横幅动画 WebP 尺寸为 {img.size}，期望 {(WIDTH, HEIGHT)}")
        except Exception as exc:  # Pillow 对损坏文件抛出的异常类型不固定
            fails.append(f"横幅动画 WebP 无法解码：{exc}")
        if size > MAX_WEBP_BYTES:
            fails.append(f"横幅动画 WebP 体积 {size >> 20} MiB 超过 {MAX_WEBP_BYTES >> 20} MiB 上限")

    if not FALLBACK_PATH.is_file() or FALLBACK_PATH.stat().st_size == 0:
        fails.append(f"缺少 {FALLBACK_PATH.relative_to(REPO)}")
    else:
        size = FALLBACK_PATH.stat().st_size
        try:
            with Image.open(FALLBACK_PATH) as img:
                if img.size != (WIDTH, HEIGHT):
                    fails.append(f"横幅静态降级 PNG 尺寸为 {img.size}，期望 {(WIDTH, HEIGHT)}")
                if img.format != "PNG":
                    fails.append(f"横幅静态降级实际格式为 {img.format}，期望 PNG")
                used = _colors_used(img)
                if used > colors:
                    fails.append(f"横幅静态降级实际用色 {used} 超过 {colors} 色上限")
                print(f"{FALLBACK_PATH.name}：{img.size[0]}×{img.size[1]}，{img.format}，"
                      f"{used} 色，{size >> 10} KiB")
        except Exception as exc:
            fails.append(f"横幅静态降级 PNG 无法解码：{exc}")
        if size > MAX_FALLBACK_BYTES:
            fails.append(f"横幅静态降级 PNG 体积 {size >> 20} MiB 超过 {MAX_FALLBACK_BYTES >> 20} MiB 上限")

    return fails


def main() -> int:
    parser = argparse.ArgumentParser(
        description="生成 assets/banner/pixel-flower-landscape-64color.webp 与 "
                    "assets/banner/pixel-flower-landscape-64color.png")
    parser.add_argument("--source", help="源视频路径，例如 pixel-flower-landscape.mp4")
    parser.add_argument("--still-source", default=str(DEFAULT_STILL_SOURCE),
                        help="静态降级源图路径，默认取受控源目录里的 png")
    parser.add_argument("--colors", type=int, default=PALETTE_COLORS,
                        help=f"静态降级减色色数，默认 {PALETTE_COLORS}")
    parser.add_argument("--start", type=float, default=0.0, help="片段起点（秒），默认 0")
    parser.add_argument("--duration", type=float, default=DEFAULT_SECONDS,
                        help=f"片段长度（秒），默认 {DEFAULT_SECONDS}")
    parser.add_argument("--ffmpeg", help="ffmpeg 可执行文件路径")
    parser.add_argument("--ffprobe", help="ffprobe 可执行文件路径")
    parser.add_argument("--check", action="store_true", help="只校验现有资源，不生成")
    args = parser.parse_args()

    cfg = toolchain.load_config()

    if args.check:
        fails = verify(args.colors)
        for msg in fails:
            print(f"::error::{msg}")
        if fails:
            return 1
        print("横幅媒体校验通过")
        return 0

    if not args.source:
        parser.error("生成模式需要 --source 指定源视频")

    source = Path(args.source)
    if not source.is_file():
        raise SystemExit(f"源视频不存在：{source}")

    still_source = Path(args.still_source)
    if not still_source.is_file():
        raise SystemExit(f"静态降级源图不存在：{still_source}")

    ffmpeg = toolchain.find_tool("ffmpeg", args.ffmpeg, cfg)
    ffprobe = toolchain.find_tool("ffprobe", args.ffprobe, cfg)
    if not ffmpeg:
        raise SystemExit(toolchain.describe_missing("ffmpeg"))
    if not ffprobe:
        raise SystemExit(toolchain.describe_missing("ffprobe"))

    info = probe(ffprobe, source)
    print(f"源视频：{info['width']}×{info['height']}，{info['duration']:.2f}s，{info['fps']:.2f} fps")

    start = max(0.0, min(args.start, max(0.0, info["duration"] - 1.0)))
    seconds = args.duration or min(DEFAULT_SECONDS, info["duration"])
    seconds = max(1.0, min(seconds, info["duration"] - start))

    filters = crop_filter(info["width"], info["height"])
    WEBP_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"生成动画 WebP：{start:.2f}s 起 {seconds:.2f}s，{FPS} fps，质量 {QUALITY}…")
    build_webp(ffmpeg, source, filters, start, seconds)

    print(f"生成静态降级 PNG：从 {still_source.name} 缩放后减色到 {args.colors} 色…")
    build_still(still_source, args.colors)

    fails = verify(args.colors)
    for msg in fails:
        print(f"::error::{msg}")
    if fails:
        return 1
    print("横幅媒体生成完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())