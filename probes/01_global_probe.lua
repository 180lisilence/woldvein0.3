-- ============================================================
-- 全局对象探针 v1.0
-- 功能：遍历 _G 中所有 table，递归输出结构（只读，不修改任何东西）
-- 深度：3层
-- 每个table最多输出：50个字段
-- 使用：复制本文件全部内容，在修改器的Lua执行框中粘贴执行
-- ============================================================

local result = {}
local visited = {}
local DEPTH_LIMIT = 3
local FIELDS_PER_TABLE = 50

local function pad(depth)
    return string.rep("  ", depth)
end

local function dump_value(v)
    local t = type(v)
    if t == "number" then
        return tostring(v) .. " (number)"
    elseif t == "string" then
        local s = v
        if #s > 60 then s = s:sub(1, 60) .. "..." end
        return '"' .. s .. '" (string)'
    elseif t == "boolean" then
        return tostring(v) .. " (boolean)"
    elseif t == "function" then
        return "function"
    elseif t == "userdata" then
        return "userdata"
    elseif t == "thread" then
        return "thread"
    elseif t == "nil" then
        return "nil"
    else
        return t
    end
end

local function dump_table(name, tbl, depth)
    if depth > DEPTH_LIMIT then return end
    if visited[tbl] then return end
    visited[tbl] = true

    -- 统计字段数
    local total = 0
    for k, v in pairs(tbl) do total = total + 1 end

    -- 统计数值字段数（可能是可修改的属性）
    local num_count = 0
    local func_count = 0
    local table_count = 0
    for k, v in pairs(tbl) do
        local t = type(v)
        if t == "number" then num_count = num_count + 1
        elseif t == "function" then func_count = func_count + 1
        elseif t == "table" then table_count = table_count + 1 end
    end

    table.insert(result, string.format(
        "%s[%s] table  字段:%d  数值:%d  函数:%d  子表:%d",
        pad(depth), name, total, num_count, func_count, table_count
    ))

    if depth >= DEPTH_LIMIT then return end

    -- 收集字段并排序（数值优先，然后字符串，然后其他）
    local fields = {}
    for k, v in pairs(tbl) do
        table.insert(fields, {key = k, val = v, key_type = type(k)})
    end

    -- 排序：字符串key按字母序，数值key按大小
    table.sort(fields, function(a, b)
        if a.key_type == "string" and b.key_type == "string" then
            return a.key < b.key
        elseif a.key_type == "number" and b.key_type == "number" then
            return a.key < b.key
        elseif a.key_type == "string" then
            return true
        else
            return false
        end
    end)

    local idx = 0
    for _, f in ipairs(fields) do
        idx = idx + 1
        if idx > FIELDS_PER_TABLE then
            table.insert(result, pad(depth + 1) .. "... (还有 " .. (total - FIELDS_PER_TABLE) .. " 个字段省略)")
            break
        end

        local k_str = tostring(f.key)
        local v = f.val
        local vt = type(v)

        if vt == "table" then
            -- 子表递归
            if not visited[v] then
                dump_table(k_str, v, depth + 1)
            else
                table.insert(result, pad(depth + 1) .. "[" .. k_str .. "] table (已访问，跳过)")
            end
        else
            table.insert(result, pad(depth + 1) .. k_str .. " = " .. dump_value(v))
        end
    end
end

-- 跳过的系统/Lua标准库表
local SKIP = {
    ["_G"] = true,
    ["_VERSION"] = true,
    ["package"] = true,
    ["io"] = true,
    ["os"] = true,
    ["table"] = true,
    ["string"] = true,
    ["math"] = true,
    ["coroutine"] = true,
    ["debug"] = true,
    ["bit"] = true,
    ["bit32"] = true,
    ["utf8"] = true,
    ["jit"] = true,
    ["ffi"] = true,
    ["C"] = true,
}

-- 跳过以双下划线开头的内部变量
local function should_skip(name)
    if SKIP[name] then return true end
    if name:sub(1, 2) == "__" then return true end
    return false
end

table.insert(result, "============================================================")
table.insert(result, "  全局对象探针 v1.0")
table.insert(result, "  深度限制: " .. DEPTH_LIMIT .. "层")
table.insert(result, "  每表字段上限: " .. FIELDS_PER_TABLE)
table.insert(result, "============================================================")
table.insert(result, "")

-- 收集所有全局table
local globals = {}
for k, v in pairs(_G) do
    if type(v) == "table" and not should_skip(k) then
        table.insert(globals, {name = k, tbl = v})
    end
end

table.sort(globals, function(a, b) return a.name < b.name end)

table.insert(result, "找到 " .. #globals .. " 个全局 table（已跳过Lua标准库和内部变量）")
table.insert(result, "")

-- 逐个dump
for _, g in ipairs(globals) do
    dump_table(g.name, g.tbl, 0)
    table.insert(result, "")
end

table.insert(result, "============================================================")
table.insert(result, "  探针结束")
table.insert(result, "============================================================")

-- 返回结果（修改器会捕获return值作为执行结果）
return table.concat(result, "\n")
