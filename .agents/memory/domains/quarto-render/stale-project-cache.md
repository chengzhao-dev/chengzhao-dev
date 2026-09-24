---
name: stale-project-cache
description: 经验教训：quarto render 无报错但产物是旧内容，根因是 .quarto/project-cache 过期且被锁，清缓存即恢复。
metadata:
  short-description: 项目缓存过期教训
  summary: 渲染无报错但产物过期的根因与清缓存处理步骤
  triggers:
    - 缓存
    - project-cache
    - deno-kv
    - 渲染错误
    - 过滤器未生效
---

# 项目缓存过期导致渲染结果错误

- 日期：2026-09-23
- 关键词：quarto render、project-cache、deno-kv、过滤器未生效、表格多行

## 现象

`quarto render` 正常结束、不报任何错误，但输出内容是旧的渲染路径：当时的表格过滤器没有把推荐仓库表格改写成单行 HTML，README 里出现多行 HTML 表格（GitHub 会把表格切成普通文本）。源文件、`_quarto.yml`、Lua 过滤器、Quarto 版本（1.10.18）均无问题——用相同的格式参数手动跑 `quarto pandoc` 或渲染独立 probe 文件都能得到正确输出。（注：该过滤器已于 2026-09 随推荐项目列表化移除，本条沉淀的是「项目缓存过期」这一通用经验。）

## 根因

`.quarto/project-cache/`（deno KV）里存有过期的项目缓存，且残留的 Quarto 会话把 `deno-kv-file` 锁住，`rm -rf .quarto` 会报 `Device or resource busy`。缓存过期时渲染仍会「成功」，但产出与源文件不一致，且 diff 里出现大段意料之外的变化。

## 处理方式

1. 确认没有残留 Quarto 进程占用 `.quarto/`（此前会话的 `quarto preview` 可能未完全退出）。
2. 删除 `.quarto/` 与 `.quarto-cache/`（锁住的文件等几秒后重试）。
3. 重新 `quarto render`，核对输出恢复正常。

## 排查信号

遇到「渲染无报错但产物与源文件明显不符」「新增的 Lua 过滤器像是没运行」时，先清缓存再排查过滤器本身；用 `quarto pandoc` + 独立 probe 文件可以快速把「过滤器问题」和「项目缓存问题」区分开：probe 正确而项目渲染错误，基本就是缓存。
