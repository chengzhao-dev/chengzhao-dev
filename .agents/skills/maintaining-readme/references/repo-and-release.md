# 发布与提交规范

本文件只写流程与规范；分支职责、SVG 清单与生成顺序等事实见 `.agents/knowledge/repo-layout/branches-workflows.md`。

## 横幅重新生成

改参数或素材后重新生成（不手改生成物）：

```bash
python .agents/skills/designing-visuals/scripts/media/gen_banner.py --source assets/source/pixel-flower-landscape/pixel-flower-landscape.mp4
python .agents/skills/designing-visuals/scripts/media/gen_banner.py --check    # 只校验现有资源
```

`--start`、`--duration`、`--still-source`、`--colors`、`--ffmpeg`、`--ffprobe` 可按需覆盖；生成参数、体积上限与色数依据见 `.agents/knowledge/visual-design/banner-media.md`。

## 发布检查

- `snake.yml` 发布前必须检查六个 SVG 都存在且非空，缺任何一个都要让 workflow 失败，避免用不完整的 `dist` 覆盖 `output` 分支。
- 不要把 README 复制到其他分支；统计卡与贡献图脚本不要拆成两个各自推送 `output` 的 workflow。

## 提交规范

- 未经明确授权不执行 `git commit` 与 `git push`；渲染与校验在本地完成。
- 提交信息使用 Conventional Commits 前缀：`docs` 用于内容、文案、展示与规范文档，`chore` 用于构建、工具链与 CI 配置；本仓库不把已有内容的维护调整标记为 `feat`。
- 按主题拆分提交：README 展示相关（`content/`、`index.qmd`、`assets/`、`README.md`）归 `docs`；渲染与发布工具链（`scripts/`、`.github/workflows/`、`config.toml`、`_quarto.yml`、`_templates/`、`.gitignore`）归 `chore`；Agent 工作区规则（`AGENTS.md`、`.agents/`）归 `docs`。每个提交只包含主题相关的文件。
- `README.md` 是生成物，必须与其源文件（`content/`、`index.qmd`、`_quarto.yml`、`_templates/`）出现在同一个提交里，不能单独提交。
- 推送前在本地完成全部校验：`quarto render` 后确认 README 与源一致、`git diff --check`、敏感信息与本机路径扫描，确认没有本地预览产物、Quarto 缓存、凭证与密钥。
