---
name: banner-media
description: 横幅媒体的事实与参数：WebP + 静态降级的依据、源素材与输出资源规格、FFmpeg 生成参数、体积上限与静态可读要求。
metadata:
  short-description: 横幅媒体参数事实
  summary: 横幅 WebP/静态降级的素材规格、编码参数、体积上限与重新生成入口
  triggers:
    - 横幅
    - banner
    - webp
    - ffmpeg
    - 64color
    - 体积上限
---

# 横幅媒体参数

顶部横幅是「动画 WebP 优先 + 静态 PNG 降级」的 `<picture>` 结构，由
`.agents/skills/designing-visuals/scripts/media/gen_banner.py` 从受控目录里的像素风花朵山水素材生成。

## 为什么是 WebP + 静态降级

GitHub 官方文档列出的仓库图片格式是 PNG、JPG、GIF、PSD、SVG，**没有把 WebP 列为稳定保证**。
因此动画 WebP 只作增强展示：浏览器支持 `<source type="image/webp">` 时播放动画，
不支持或图片加载失败时，`<img>` 指向的静态 PNG 保证横幅仍然完整可读。

降级不是可选优化。README 里少写 `<picture>` 或删掉 fallback，都会让不支持 WebP 的访客看到破图，
`.github/workflows/readme.yml` 会拦截这两种情况。

静态降级用 PNG 而不是 JPEG：素材是像素画，色块边界清晰，PNG 的无损调色板编码既贴合像素质感，
又能在减色后把体积压到 JPEG 同级。

## 源素材

两个源文件都放在受控目录 `assets/source/pixel-flower-landscape/`：

| 文件 | 作用 |
|------|------|
| `pixel-flower-landscape.mp4` | 动画源，1280×720、24 fps、约 10 秒 |
| `pixel-flower-landscape.png` | 静态降级源，2048×1152、RGB |

## 输出资源

README 直接引用的两个文件放二级目录 `assets/banner/`，文件名里的 `-64color`
标明静态降级被减色到 64 色：

| 资源 | 尺寸 | 内容 | 体积上限 |
|------|------|------|----------|
| `assets/banner/pixel-flower-landscape-64color.webp` | 1280×720 | 动画，60 帧 / 约 6 秒，无限循环 | 8 MiB |
| `assets/banner/pixel-flower-landscape-64color.png` | 1280×720 | 静态源图缩放后减色到 64 色 | 2 MiB |

## 生成参数

- 源视频本身就是 1280×720 的 16:9，`crop_filter` 判定无需裁切，直接按目标尺寸缩放。
- 取前 6 秒，抽成 10 fps，共 60 帧。源视频帧率是 24 fps，全量保留会让 WebP 体积翻倍，
  而画面只是缓慢流动的水面与花丛，10 fps 已能看出动感。
- 编码用 `libwebp_anim`，质量 55，`-compression_level 6`，`-loop 0`（无限循环），`-an` 丢弃音轨。
- 质量 55 是实测的平衡点：1280×720 下约 3.0 MiB。质量提到 75 会大幅增长，
  而这幅画在 README 的显示宽度下看不出差别。
- 静态降级先把源 PNG 用 LANCZOS 缩放到 1280×720，再用 Pillow `MEDIANCUT` 减色到 64 色，
  `dither=NONE` 不做抖动，保住像素画的离散色块；实测约 270 KiB。
- 减色色数取 64：32 色在天空云层与水面高光处会出现可见断层，64 色的渐变过渡平滑，
  体积仍在 2 MiB 上限内。改色数用 `--colors` 覆盖，并把输出文件名里的 `-64color` 一起改掉。

## 重新生成

重新生成的命令与覆盖参数属于流程，见技能 `maintaining-readme` 的 `references/repo-and-release.md`；脚本会先校验输出可解码、尺寸正确、动画时长落在 4–10 秒区间、静态降级用色不超过目标色数、体积不超上限，不通过就直接失败。

FFmpeg/FFprobe 的来源与版本见 `.agents/skills/designing-visuals/scripts/media/bootstrap_media.py`：固定版本、固定 URL、固定 SHA-256，
下载到被忽略的 `.agents/skills/designing-visuals/scripts/media/tool-cache/`（路径由根目录 `config.toml` 的 `tool_cache_dir` 决定），仓库里只保留可复现的脚本。

## 静态可读要求

动画只是氛围，被剥离或冻结时画面必须仍然成立。横幅不放标题、参数或个人姓名，
身份和方向由下方正文承担；图片的 `alt` 描述画面本身，不写「横幅」「装饰图」这类空指代。