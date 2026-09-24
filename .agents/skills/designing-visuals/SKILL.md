---
name: designing-visuals
description: 设计 GitHub Profile README 的视觉组件：动画 WebP 横幅与静态降级、花丛色板、Shields 徽章与移动端布局。
metadata:
  short-description: Profile README 视觉与组件规范
  summary: 横幅、色板、Shields 组件与推荐项目列表样式的唯一标准
  triggers:
    - 横幅
    - 色板
    - 徽章
    - 组件
    - 视觉
    - 推荐项目
    - picture
  paths:
    - "content/**"
    - "assets/**"
    - "index.qmd"
    - ".agents/skills/designing-visuals/scripts/**"
---

# Profile README 视觉规范

## 适用范围

仅适用于 GitHub Profile README 的视觉资源与组件组织，并承载「推荐项目列表样式」的唯一标准。文案见 `writing-readme`；渲染与发布见 `maintaining-readme`；色板、信任层级与横幅参数按 `knowledge/KNOWLEDGE.md` 索引读取；命名结构、入口文档写法与删改重组见 `governing-agents`。

## 顶部横幅

横幅是页面第一屏唯一的装饰元素，只负责建立氛围，不承载信息。

- 横幅是「动画 WebP 优先 + 静态 PNG 降级」的 `<picture>` 结构：WebP 作 `<source>`，静态 PNG 作 `<img>` 降级分支。GitHub 官方列出的仓库图片格式没有 WebP，静态降级不是可选项，缺分支会让不支持 WebP 的访客看到破图。
- 画布固定为 1280×720，页面里以 `width="100%"` 自适应；画面主体在 360 像素宽下必须仍可辨认。
- 源素材按 16:9 居中裁切，不裁掉主体、不拉伸变形；不写标题、参数与个人姓名，不叠加文字、logo 或水印。
- 画面取自像素风花朵山水素材，色板见下节「配色」；只有单份横幅资源，不做深浅色两版。
- 不出现霓虹色、发光描边、扫描线、网格、故障纹理等赛博朋克元素，也不做夜景化处理。
- 动效与降级帧由本技能 `scripts/media/gen_banner.py` 生成：改参数改脚本后重新生成，不手改生成物；动效由视频本身承载，不用 SMIL、CSS 动画或外链视频，动画里不放必须阅读的信息。
- 帧率、循环时长、减色上限等生成参数见 `knowledge/visual-design/banner-media.md`，本技能不重复。

## 配色

- 整体使用与横幅画面一致的明亮花丛色板：近白／浅米底、深苔绿或暖褐文字，强调色取花品红、溪流蓝、叶绿与暖黄。具体 token 见 `knowledge/visual-design/bright-palette.md`。
- 徽章不使用深色底 One Dark 配色：明亮横幅下深色徽章会形成割裂感；不使用霓虹色、发光和彩虹渐变，同一页面保持同一套色值。

## 组件选择

- 技术栈用 Shields.io 徽章，按「编程语言」「工具与工作流」等维度拆成 `###` 子标题，每个子标题下只放对应卡片；同类徽章 `style` 必须统一，不同类可分别选择。
- 贡献图与「账号统计」「常用语言」统计卡只能是静态 SVG，必须提供文字说明或主页链接作为降级；浅色/深色两版由 `<picture>` 按 `prefers-color-scheme` 切换，只引用本仓库 `output` 分支自建的 SVG，不用 `github-readme-stats*.vercel.app` 之类的公共实例，深色 token 见 bright-palette 知识条目。
- 贡献图的月份与星期标注由本技能 `scripts/activity/add_labels.py` 叠加，只占网格四周留白，不覆盖动画主体，也不在 README 里手工写死日期。
- 只允许 GitHub 官方托管资源与成熟公开徽章服务，不引入单一来源、无法自建的动态服务；允许与禁止清单见 `knowledge/component-trust/trust-tiers.md`。
- README 不嵌入 JavaScript、动态游戏或任何需要客户端执行的代码。

## 推荐项目列表样式

推荐项目的展示形式以本节为唯一标准。说明句与指针的字数区间见 `writing-readme` 的「字数区间」，本节不重复。

- 展示形式用无序列表，不用表格：每条一行 `- [仓库名](仓库 URL) —— 一句话说明`，窄屏下自然折行，不需要列宽控制。
- 说明句写在列表上方（1–2 句），并在这句里一并给出「全部公开仓库」与本仓库 `ARCHITECTURE.md` 的指针；列表下方不再补句。
- 条目顺序：本 Profile 仓库在前，其余按长期维护的重要度排；只列真实在维护的仓库。
- 一句话说明写「这是什么 + 用途或给谁用」，不暴露源码树、内部目录名与实现细节；最多 1 个行内链接。
- 不放「最近更新」「协议」等指标徽章：数值随时变化且 CI 无法核实；GitHub 官方由 Profile 的 Pinned 仓库承担推荐职责（<https://docs.github.com/en/github/setting-up-and-managing-your-github-profile/about-your-profile>）。
- 不使用第三方项目卡，不嵌 JavaScript；不引用 `opengraph.githubassets.com` 预览图。

## 布局

- 组件顺序服务于叙事：横幅、你好、技术栈、推荐项目、过去一年贡献、GitHub 统计、与我相关；区域之间用标题和留白分隔。
- 不用表格承载「名称 + 长描述」：列宽由渲染器决定，窄屏下必然难看；推荐项目用无序列表，窄屏自然折行。

## 明亮风格

页面观感取自横幅画面，落成可复用的判断依据：

- 观感关键词：新海诚式电影感——暖金柔光、春叶绿、溪流蓝、花品红；明亮、低饱和、浅底深字。深色主题对应「蓝调时刻」：深蓝灰画布、近白文字、加亮强调色；「新海诚式」是视觉来源而非官方规范，色值统一走 token。
- 层次：横幅是前景花丛 → 中景溪流 → 远景山雾，页面沿同一条视线推进：氛围 → 身份 → 能力 → 作品 → 数据 → 去向；每个区域只做一件事，少堆叠、少口号，中文短句优先。

## 检查清单

- 横幅 `<picture>` 分支完整：WebP `<source>` + 带 `alt` 的静态降级 `<img>`。
- `assets/banner/pixel-flower-landscape-64color.webp` 是可解码的动画 WebP（1280×720、帧数大于 1、时长 4 至 10 秒）；同名 PNG 可解码、同为 1280×720、用色不超过 64 色，与动画取自同一构图素材。
- 横幅与降级帧由本技能 `scripts/media/gen_banner.py` 生成，没有手改生成物。
- 所有图片都有准确 `alt`，横幅的 `alt` 描述画面与动效本身。
- 统计卡浅色/深色 SVG 成对生成且都被 README 引用；深色下文字与强调色可读。
- 推荐项目满足「推荐项目列表样式」的全部条目：说明与指针在列表上方、无指标徽章、无第三方项目卡。
- 标题符合 `writing-chinese` 的标题规范。
- 横幅在 1280 与 360 像素宽度下检查：不裁切、不溢出、主体可辨认；推荐项目列表在 360 像素下无横向溢出。
- 确认没有引入 JavaScript、外链视频、第三方统计卡与赛博朋克元素；页面颜色不超过色板。