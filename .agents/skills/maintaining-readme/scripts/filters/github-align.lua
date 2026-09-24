-- GitHub 只识别 HTML 的 align 属性，但 pandoc 的 HTML 解析会把 Div 上的 align
-- 改写成 data-align，而 GitHub 的 Markdown 清洗器会直接丢掉这个属性，导致居中失效。
-- 这里把带 align 的 Div 还原成原始 HTML 块，让属性原样写入 README.md。

local function take_align(attributes)
  local align = attributes["align"] or attributes["data-align"]
  attributes["align"] = nil
  attributes["data-align"] = nil
  return align
end

local function attribute_string(el, align)
  local parts = {}

  if el.identifier ~= "" then
    parts[#parts + 1] = 'id="' .. el.identifier .. '"'
  end

  if #el.classes > 0 then
    parts[#parts + 1] = 'class="' .. table.concat(el.classes, " ") .. '"'
  end

  parts[#parts + 1] = 'align="' .. align .. '"'

  local keys = {}
  for key, _ in pairs(el.attributes) do
    keys[#keys + 1] = key
  end
  table.sort(keys)

  for _, key in ipairs(keys) do
    parts[#parts + 1] = key .. '="' .. el.attributes[key] .. '"'
  end

  return table.concat(parts, " ")
end

function Div(el)
  local align = take_align(el.attributes)
  if not align then
    return nil
  end

  local blocks = { pandoc.RawBlock("html", "<div " .. attribute_string(el, align) .. ">") }
  for _, block in ipairs(el.content) do
    blocks[#blocks + 1] = block
  end
  blocks[#blocks + 1] = pandoc.RawBlock("html", "</div>")

  return blocks
end