# 注释规范来源

以下链接为本技能注释规则的依据，2026-09 记录；访问状态以实际打开为准，链接失效时先核实来源是否迁移，再决定改规则还是换链接。规则与来源冲突时，先核实来源是否更新，再决定改规则还是换来源。

## Google 开源项目风格指南

- Python（注释与 docstring）：注释应为完整句子、解释代码无法自明的部分；docstring 规范见第 3.8 节 Comments and Docstrings。
  <https://google.github.io/styleguide/pyguide.html>
- 文档写作最佳实践：文档开头说明用途、保持简短、避免过期信息。
  <https://google.github.io/styleguide/docguide/best_practices.html>

说明：Google 官方指南没有 TOML/YAML 专章，本仓库的 TOML 与 YAML 规则取其通用原则（文件头说明用途、完整句子、紧邻代码），语法细节按下述来源。

## TOML 与 YAML 语法

- TOML 官方规范中文版：注释以 `#` 开头直至行尾。
  <https://toml.io/cn/>
- yamllint 默认规则（YAML 语法与注释习惯，如 `comments` 规则要求 `#` 后一个空格）：
  <https://yamllint.readthedocs.io/en/stable/rules.html>

## Lua 与 Python 语法

- Lua 5.4 参考手册：`--` 行注释与 `--[[ ]]` 块注释。
  <https://www.lua.org/manual/5.4/manual.html#3.1>
- Python 注释与 docstring 语法遵循上述 Google Python 指南；语言行为以官方文档为准。
  <https://docs.python.org/3/tutorial/controlflow.html#documentation-strings>
- Python Unix：可执行脚本推荐 `#!/usr/bin/env python3`。
  <https://docs.python.org/3/using/unix.html>
- Python 教程附录：Executable Python Scripts（Unix shebang 与 Windows 扩展名关联）。
  <https://docs.python.org/3/tutorial/appendix.html>
- Python Windows：Shebang lines（`python`/`py` 识别 `/usr/bin/env` 等虚拟命令，便于跨平台）。
  <https://docs.python.org/3/using/windows.html>
