"""横幅媒体的唯一参数事实源。

gen_banner.py（生成与本地校验）和 CI 的横幅校验都从本模块取规格，
避免两边各自维护一份上限值后漂移；调整横幅规格只改本文件。
编码侧参数（帧率、质量、压缩级别、循环次数）属于生成脚本，不在这里。
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
BANNER_DIR = REPO / "assets" / "banner"
WEBP_PATH = BANNER_DIR / "pixel-flower-landscape-64color.webp"
FALLBACK_PATH = BANNER_DIR / "pixel-flower-landscape-64color.png"

# 横幅在 README 里按 100% 宽度铺满，1280×720 在桌面端足够清晰，也控制住文件体积。
WIDTH, HEIGHT = 1280, 720

# 片段长度目标区间：太短看不出循环，太长会让 WebP 过大；生成默认取 6 秒。
MIN_SECONDS, MAX_SECONDS = 4.0, 10.0
DEFAULT_SECONDS = 6.0

# 静态降级减色色数：32 色在天空云层与水面高光处会出现可见断层，64 色过渡平滑。
PALETTE_COLORS = 64

# 动画 WebP 与静态降级 PNG 各自的体积上限。
MAX_WEBP_BYTES = 8 * 1024 * 1024
MAX_FALLBACK_BYTES = 2 * 1024 * 1024
