#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
woldvein Trainer v0.3 - 世界系统扩展模块

功能说明：
    独立于 advanced_tools.py 的一批「世界/城市系统」控制，避免主文件继续膨胀：

    1. 市场物价   g_LMarketManager.m_prices[trandID][solarTerm+1]（可写表）
    2. 产业链     g_BuildingIndustryChain:SetUnlockState(true) / GetIsUnlock()
    3. 流民灾害   block:GetActiveDisaster(DT_REFUGEE) -> CleanAllUnacceptedRefugees / SuppressUnacceptedRefugeesRiot
    4. 蓝图       BuildingMgr:GetBuildingList() + bld:IsBlueprint()（仅探查，合成 API 未确认）
    5. 知名度     g_LReputationMgr:ChangeReputation() + ChangeReputationBase()（双存储必须同时改）
    6. NPC 详情   g_CityManager.m_lActiveCity.m_lCityNpcMgr（仅探查，字段因版本而异）
    7. 建筑精细   BuildingMgr:GetBuildingList() -> bld:UpgradeToTop() / GM_FullAllPopulation()

设计原则：
    - 探查优先：API 未在游戏源码中完全确认的系统，先提供 probe，输出真实对象/字段/方法，供实机迭代。
    - 防御式执行：动作脚本逐项 pcall，回报成功/失败计数，不静默失败。
    - 参数注入：用 __PLACEHOLDER__ + str.replace，避免 Python % 与 Lua %d/%s 转义冲突（原 %%d bug 的同类问题）。

注意：
    - 所有脚本需在 DLL 注入并进入游戏存档后执行（g_camp 等全局对象才就绪）。
    - 统一走 execute_lua_safe（异常不崩溃）。
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.lua_engine import execute_lua_safe
from src.logger import log, log_success, log_error, log_warning


# ============================================================
# 1. 市场物价
# ============================================================

LUA_MARKET_PROBE = r"""
local ok, err = pcall(function()
    local m = g_LMarketManager
    if not m then return "[失败] 全局对象 g_LMarketManager 不存在（请先进入游戏场景）" end
    local lines = {"=== 市场管理器探查 ==="}
    table.insert(lines, "当前节气 m_solarTerm = " .. tostring(m.m_solarTerm))
    local prices = m.m_prices
    if type(prices) == "table" then
        local n = 0
        for tid, arr in pairs(prices) do
            n = n + 1
            if n <= 6 and type(arr) == "table" then
                local vals = {}
                for i = 1, #arr do vals[#vals + 1] = tostring(arr[i]) end
                table.insert(lines, "  m_prices[" .. tostring(tid) .. "] = {" .. table.concat(vals, ", ") .. "}")
            end
        end
        table.insert(lines, "m_prices 条目数 = " .. tostring(n))
    else
        table.insert(lines, "m_prices 类型 = " .. type(prices))
    end
    table.insert(lines, "")
    table.insert(lines, "=== 对象导出 ===")
    pcall(function() __trainer_dump(g_LMarketManager, lines) end)
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_MARKET_PRICE_SCALE = r"""
local ok, err = pcall(function()
    local m = g_LMarketManager
    if not m or type(m.m_prices) ~= "table" then return "[失败] g_LMarketManager.m_prices 不存在" end
    local factor = tonumber(__FACTOR__) or 1.0
    if not _G._trainer_market_backup then
        local backup = {}
        for tid, arr in pairs(m.m_prices) do
            if type(arr) == "table" then
                local copy = {}
                for i = 1, #arr do copy[i] = arr[i] end
                backup[tid] = copy
            end
        end
        _G._trainer_market_backup = backup
    end
    local changed = 0
    for tid, arr in pairs(m.m_prices) do
        if type(arr) == "table" then
            for i = 1, #arr do
                local v = tonumber(arr[i])
                if v then arr[i] = math.floor(v * factor + 0.5); changed = changed + 1 end
            end
        end
    end
    return "[成功] 市场价格已按 x" .. tostring(factor) .. " 调整（" .. tostring(changed) .. " 个价格条目）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_MARKET_PRICE_RESTORE = r"""
local ok, err = pcall(function()
    local m = g_LMarketManager
    local backup = _G._trainer_market_backup
    if not m or type(m.m_prices) ~= "table" then return "[失败] g_LMarketManager.m_prices 不存在" end
    if not backup then return "[提示] 无可还原快照（需先执行一次价格调整）" end
    for tid, arr in pairs(backup) do
        if type(m.m_prices[tid]) == "table" then
            for i = 1, #arr do m.m_prices[tid][i] = arr[i] end
        end
    end
    _G._trainer_market_backup = nil
    return "[成功] 市场价格已还原为操作前数值"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# 2. 产业链
# ============================================================

LUA_CHAIN_PROBE = r"""
local ok, err = pcall(function()
    local ch = g_BuildingIndustryChain
    if not ch then return "[失败] 全局对象 g_BuildingIndustryChain 不存在" end
    local lines = {"=== 产业链探查 ==="}
    local isUnlock = "?"
    pcall(function() if ch.GetIsUnlock then isUnlock = tostring(ch:GetIsUnlock()) end end)
    table.insert(lines, "GetIsUnlock() = " .. isUnlock)
    local ok2, chains = pcall(function() return ch:GetChainsInHandbook() end)
    if ok2 and type(chains) == "table" then
        table.insert(lines, "GetChainsInHandbook() 返回 " .. tostring(#chains) .. " 项")
    end
    table.insert(lines, "")
    table.insert(lines, "=== 对象导出 ===")
    pcall(function() __trainer_dump(g_BuildingIndustryChain, lines) end)
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_CHAIN_UNLOCK_ALL = r"""
local ok, err = pcall(function()
    local ch = g_BuildingIndustryChain
    if not ch then return "[失败] g_BuildingIndustryChain 不存在（请先进入游戏场景）" end

    local log = {}

    -- 1) 让“产业链关系是否激活”的判定恒为 true（加成生效）。
    --    注意：CalBuildingChainActived 会在建筑变化时重算并覆盖 m_tbActiveChainList，
    --    只改数据会被覆盖回 false，所以必须在类方法层做判定覆盖。
    local hooked = false
    local mt = getmetatable(ch)
    local cls = mt and mt.__index
    if cls then
        if not cls.__trainer_chain_orig then
            cls.__trainer_chain_orig = cls._GetbActivedRelation
        end
        cls._GetbActivedRelation = function(self, nBlockID, szGDPL) return true end
        hooked = true
    end
    table.insert(log, "关系判定Hook=" .. tostring(hooked))

    -- 2) 顺带把当前所有地块的激活表填满（立即生效）
    local filled = 0
    local gdplMap = ch.m_tbGDPL2ChainKey or {}
    local blocks = (g_blockMgr and g_blockMgr.GetAllBlocks and g_blockMgr:GetAllBlocks()) or {}
    if type(ch.m_tbActiveChainList) ~= "table" then ch.m_tbActiveChainList = {} end
    for bid, _ in pairs(blocks) do
        if type(ch.m_tbActiveChainList[bid]) ~= "table" then ch.m_tbActiveChainList[bid] = {} end
        for gdpl, _ in pairs(gdplMap) do
            ch.m_tbActiveChainList[bid][gdpl] = true
            filled = filled + 1
        end
    end
    table.insert(log, "填充激活项=" .. tostring(filled))

    -- 3) 解锁开关（原本默认就是 true，这里保证为 true）
    pcall(function() ch:SetUnlockState(true) end)
    local isUnlock = "?"
    pcall(function() isUnlock = tostring(ch:GetIsUnlock()) end)
    table.insert(log, "GetIsUnlock=" .. isUnlock)

    return "[成功] 产业链已解锁（" .. table.concat(log, "，") .. "）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# 3. 流民灾害
# ============================================================

LUA_REFUGEE_BLOCKS = r"""
local function __trainer_get_blocks()
    local blocks = nil
    if g_blockMgr and g_blockMgr.GetAllBlocks then
        pcall(function() blocks = g_blockMgr:GetAllBlocks() end)
    end
    if type(blocks) ~= "table" and g_blockMgr and g_blockMgr.GetBlock then
        local b = g_blockMgr:GetBlock(block_define and block_define.CAMP_ID or 1)
        if b then blocks = {b} end
    end
    return blocks
end
"""

LUA_REFUGEE_PROBE = LUA_REFUGEE_BLOCKS + r"""
local ok, err = pcall(function()
    local lines = {"=== 流民灾害探查 ==="}
    if not g_blockMgr then return "[失败] g_blockMgr 不存在" end
    local dt = game_world_define and game_world_define.DisasterType
    if not dt then return "[失败] game_world_define.DisasterType 不存在" end
    table.insert(lines, "DT_REFUGEE = " .. tostring(dt.DT_REFUGEE))
    local blocks = __trainer_get_blocks()
    local found = 0
    if type(blocks) == "table" then
        for id, block in pairs(blocks) do
            if type(block) == "table" and block.GetActiveDisaster then
                local ok2, dis = pcall(function() return block:GetActiveDisaster(dt.DT_REFUGEE) end)
                if ok2 and dis then
                    found = found + 1
                    local num = "?"
                    pcall(function() if dis.GetUnacceptedRefugeesNum then num = tostring(dis:GetUnacceptedRefugeesNum()) end end)
                    table.insert(lines, "  地块[" .. tostring(id) .. "] 流民灾害进行中，未接纳流民 = " .. num)
                end
            end
        end
    end
    if found == 0 then table.insert(lines, "（未发现进行中的流民灾害）") end
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_REFUGEE_CLEAR = LUA_REFUGEE_BLOCKS + r"""
local ok, err = pcall(function()
    if not g_blockMgr then return "[失败] g_blockMgr 不存在" end
    local dt = game_world_define and game_world_define.DisasterType
    if not dt then return "[失败] game_world_define.DisasterType 不存在" end
    local blocks = __trainer_get_blocks()
    local done = 0
    if type(blocks) == "table" then
        for _, block in pairs(blocks) do
            if type(block) == "table" and block.GetActiveDisaster then
                local ok2, dis = pcall(function() return block:GetActiveDisaster(dt.DT_REFUGEE) end)
                if ok2 and dis then
                    pcall(function() if dis.CleanAllUnacceptedRefugees then dis:CleanAllUnacceptedRefugees() end end)
                    pcall(function() if dis.SuppressUnacceptedRefugeesRiot then dis:SuppressUnacceptedRefugeesRiot() end end)
                    pcall(function() if dis.SubsideUnacceptedRefugeesRiot then dis:SubsideUnacceptedRefugeesRiot() end end)
                    done = done + 1
                end
            end
        end
    end
    return "[成功] 已处理 " .. tostring(done) .. " 处流民灾害（清零未接纳流民 + 平息暴动）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# 4. 蓝图（仅探查）
# ============================================================

LUA_BLUEPRINT_PROBE = r"""
local ok, err = pcall(function()
    local lines = {"=== 蓝图系统探查 ==="}
    local bm = g_BuildingWorldModule and g_BuildingWorldModule.BuildingMgr
    if not bm then return "[失败] BuildingMgr 不存在" end
    local list = nil
    pcall(function() if bm.GetBuildingList then list = bm:GetBuildingList() end end)
    local total, bp = 0, 0
    if type(list) == "table" then
        for _, sub in pairs(list) do
            if type(sub) == "table" then
                for uuid, bld in pairs(sub) do
                    if type(bld) == "table" then
                        total = total + 1
                        local isBp = false
                        pcall(function() if bld.IsBlueprint then isBp = bld:IsBlueprint() end end)
                        if isBp then
                            bp = bp + 1
                            if bp <= 5 then
                                local status = tostring(bld.m_nStatus or bld.status or "?")
                                table.insert(lines, "  蓝图 " .. tostring(uuid) .. " status=" .. status)
                            end
                        end
                    end
                end
            end
        end
    end
    table.insert(lines, "建筑总数 = " .. tostring(total) .. "，其中蓝图 = " .. tostring(bp))
    table.insert(lines, "（蓝图合成 API 未在游戏源码中确认，本面板仅探查）")
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# 5. 知名度（双存储）
# ============================================================

LUA_REPUTATION_PROBE = r"""
local ok, err = pcall(function()
    local rep = g_LReputationMgr
    if not rep then return "[失败] g_LReputationMgr 不存在（请先进入游戏场景）" end
    local lines = {"=== 知名度探查 ==="}
    local cur = "?"
    pcall(function() if rep.GetReputation then cur = tostring(rep:GetReputation()) end end)
    table.insert(lines, "当前知名度 GetReputation() = " .. cur)
    local methods = {}
    for k, v in pairs(rep) do
        if type(v) == "function" then methods[#methods + 1] = k end
    end
    table.sort(methods)
    table.insert(lines, "方法: " .. table.concat(methods, ", "))
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_REPUTATION_ADD = r"""
local ok, err = pcall(function()
    local rep = g_LReputationMgr
    if not rep then return "[失败] g_LReputationMgr 不存在" end
    local delta = tonumber(__DELTA__) or 0
    if delta == 0 then return "[失败] 增量无效" end
    local before = 0
    pcall(function() if rep.GetReputation then before = rep:GetReputation() end end)
    local okA = pcall(function() if rep.ChangeReputation then rep:ChangeReputation(delta) end end)
    local okB = pcall(function() if rep.ChangeReputationBase then rep:ChangeReputationBase(delta) end end)
    local after = before
    pcall(function() if rep.GetReputation then after = rep:GetReputation() end end)
    return "[成功] 知名度 " .. tostring(delta) .. "（" .. tostring(before) .. " -> " .. tostring(after) .. "）"
        .. " 双存储: ChangeReputation=" .. tostring(okA) .. " ChangeReputationBase=" .. tostring(okB)
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# 6. NPC 详情（仅探查）
# ============================================================

LUA_NPC_DETAIL_PROBE = r"""
local ok, err = pcall(function()
    local lines = {"=== NPC/城市管理器探查 ==="}
    table.insert(lines, "g_CityManager: " .. type(g_CityManager))
    if g_CityManager then
        pcall(function() __trainer_dump(g_CityManager, lines) end)
        local city = nil
        pcall(function() city = g_CityManager:GetActiveCity() end)
        table.insert(lines, "")
        table.insert(lines, "GetActiveCity(): " .. type(city))
        if city then pcall(function() __trainer_dump(city, lines) end) end
        local infos = nil
        pcall(function() infos = g_CityManager:GetCityInfoList() end)
        table.insert(lines, "GetCityInfoList(): " .. type(infos))
        if type(infos) == "table" then
            local n = 0
            for k, v in pairs(infos) do
                n = n + 1
                if n <= 2 then
                    table.insert(lines, "-- [城市信息] " .. tostring(k))
                    pcall(function() __trainer_dump(v, lines) end)
                end
            end
            table.insert(lines, "城市信息条数 = " .. tostring(n))
        end
        if type(g_CityManager.m_lsCityInfo) == "table" then
            local c = 0
            for k, v in pairs(g_CityManager.m_lsCityInfo) do
                c = c + 1
                if c <= 2 then
                    table.insert(lines, "-- [m_lsCityInfo] " .. tostring(k))
                    pcall(function() __trainer_dump(v, lines) end)
                end
            end
        end
    end
    table.insert(lines, "")
    table.insert(lines, "=== 含 Npc/NPC 的全局 ===")
    for k, v in pairs(_G) do
        if string.find(k, "Npc") or string.find(k, "NPC") then
            table.insert(lines, "  " .. k .. " (" .. type(v) .. ")")
            if (k == "g_LNPCManager" or k == "g_LSightSeeingNPCMgr") and v then
                pcall(function() __trainer_dump(v, lines, "      ") end)
            end
        end
    end
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# 7. 建筑精细操作
# ============================================================

LUA_BUILDING_DETAIL = r"""
local ok, err = pcall(function()
    local lines = {"=== 建筑明细 ==="}
    local bm = g_BuildingWorldModule and g_BuildingWorldModule.BuildingMgr
    if not bm or not bm.GetBuildingList then return "[失败] BuildingMgr.GetBuildingList 不可用" end
    local list = bm:GetBuildingList()
    if type(list) ~= "table" then return "[诊断] GetBuildingList 返回 " .. type(list) end
    local total, shown = 0, 0
    local sample = nil
    for nBlock, sub in pairs(list) do
        if type(sub) == "table" then
            for uuid, bld in pairs(sub) do
                total = total + 1
                if not sample and type(bld) == "table" then sample = bld end
                if shown < 12 and type(bld) == "table" then
                    shown = shown + 1
                    local lv = tostring(bld.nAddRangeLevel or "?")
                    local gdpKey = tostring(bld.m_szGDPKey or "?")
                    local status = tostring(bld.m_nStatus or "?")
                    table.insert(lines, "  地块" .. tostring(nBlock) .. " uuid=" .. tostring(uuid)
                        .. " 加成等级=" .. lv .. " GDPKey=" .. gdpKey .. " 状态=" .. status)
                end
            end
        end
    end
    table.insert(lines, "建筑总数 = " .. tostring(total) .. "（仅显示前 12 个）")
    if sample then
        table.insert(lines, "")
        table.insert(lines, "=== 抽样建筑导出（找等级/GDPL getter）===")
        pcall(function() __trainer_dump(sample, lines) end)
    end
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_BUILDING_TOP_ALL = r"""
local ok, err = pcall(function()
    local bm = g_BuildingWorldModule and g_BuildingWorldModule.BuildingMgr
    if not bm or not bm.GetBuildingList then return "[失败] BuildingMgr 不可用" end
    local list = bm:GetBuildingList()
    local done, fail = 0, 0
    for _, sub in pairs(list or {}) do
        if type(sub) == "table" then
            for _, bld in pairs(sub) do
                if type(bld) == "table" and bld.UpgradeToTop then
                    if pcall(function() bld:UpgradeToTop() end) then done = done + 1 else fail = fail + 1 end
                end
            end
        end
    end
    return "[成功] 建筑升级到顶：成功 " .. tostring(done) .. "，失败 " .. tostring(fail)
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_BUILDING_FULL_POP = r"""
local ok, err = pcall(function()
    local bm = g_BuildingWorldModule and g_BuildingWorldModule.BuildingMgr
    if not bm or not bm.GetBuildingList then return "[失败] BuildingMgr 不可用" end
    local list = bm:GetBuildingList()
    local done = 0
    for _, sub in pairs(list or {}) do
        if type(sub) == "table" then
            for _, bld in pairs(sub) do
                if type(bld) == "table" and bld.GM_FullAllPopulation then
                    if pcall(function() bld:GM_FullAllPopulation() end) then done = done + 1 end
                end
            end
        end
    end
    return "[成功] 已对 " .. tostring(done) .. " 个建筑执行满人口（GM_FullAllPopulation）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# Python 封装
# ============================================================

def probe_market():
    """市场物价探查（诊断用）"""
    return execute_lua_safe(LUA_MARKET_PROBE, timeout=8.0)


def market_price_scale(factor):
    """市场价格整体缩放（factor>1 涨价，<1 降价）；首次操作自动记录还原快照"""
    log(f"调整市场价格 x{factor} ...")
    code = LUA_MARKET_PRICE_SCALE.replace("__FACTOR__", str(factor))
    success, result = execute_lua_safe(code, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"市场价格调整失败: {result}")
    return success, result


def market_price_restore():
    """还原市场价格为操作前数值"""
    log("还原市场价格 ...")
    success, result = execute_lua_safe(LUA_MARKET_PRICE_RESTORE, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"市场价格还原失败: {result}")
    return success, result


def probe_industry_chain():
    """产业链探查"""
    return execute_lua_safe(LUA_CHAIN_PROBE, timeout=8.0)


def unlock_industry_chain():
    """一键解锁产业链"""
    log("正在解锁产业链 ...")
    success, result = execute_lua_safe(LUA_CHAIN_UNLOCK_ALL, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"产业链解锁失败: {result}")
    return success, result


def probe_refugee():
    """流民灾害探查"""
    return execute_lua_safe(LUA_REFUGEE_PROBE, timeout=8.0)


def clear_refugee():
    """清零未接纳流民 + 平息暴动"""
    log("正在处理流民灾害 ...")
    success, result = execute_lua_safe(LUA_REFUGEE_CLEAR, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"流民灾害处理失败: {result}")
    return success, result


def probe_blueprint():
    """蓝图系统探查"""
    return execute_lua_safe(LUA_BLUEPRINT_PROBE, timeout=8.0)


def probe_reputation():
    """知名度探查"""
    return execute_lua_safe(LUA_REPUTATION_PROBE, timeout=8.0)


def add_reputation(amount=10000):
    """增加知名度（双存储：ChangeReputation + ChangeReputationBase）"""
    log(f"增加知名度 {amount} ...")
    code = LUA_REPUTATION_ADD.replace("__DELTA__", str(amount))
    success, result = execute_lua_safe(code, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"知名度修改失败: {result}")
    return success, result


def probe_npc_detail():
    """城市NPC详情探查"""
    return execute_lua_safe(LUA_NPC_DETAIL_PROBE, timeout=8.0)


def list_building_detail():
    """列出建筑明细（UUID/等级/GDPL）"""
    return execute_lua_safe(LUA_BUILDING_DETAIL, timeout=8.0)


def upgrade_all_to_top():
    """所有建筑升级到顶（UpgradeToTop）"""
    log("正在升级所有建筑到顶 ...")
    success, result = execute_lua_safe(LUA_BUILDING_TOP_ALL, timeout=10.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"建筑升级到顶失败: {result}")
    return success, result


def full_population_all():
    """所有建筑满人口（GM_FullAllPopulation）"""
    log("正在对全部建筑执行满人口 ...")
    success, result = execute_lua_safe(LUA_BUILDING_FULL_POP, timeout=10.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"建筑满人口失败: {result}")
    return success, result


# ============================================================
# 8. 灾害控制（天灾 / 人祸）
# ============================================================
# 分类依据：game_world_define.DisasterType 的字段名关键词（数值枚举未导出，运行时取）

LUA_DISASTER_TYPES = r"""
-- 实机确认的 DisasterType 枚举（2026-09-13）：0=NONE 1=FIRE 2=INSECT 3=DISEASE 4=PLAGUE
-- 5=TORNADO 6=EARTHQUAKE 7=FAMINE 8=CRIME 9=RIOT 10=THUNDER 11=DROUGHT 12=COLDWINTER
-- 13=FLOOD 14=SEVEREFROST 15=SPRINGRAIN 16=REFUGEE 17=DELUGE 18=SALT 19=SANDSTORM
local __MANMADE_NAMES = { DT_CRIME = true, DT_RIOT = true, DT_REFUGEE = true }
local __SKIP_NAMES = { DT_NONE = true, DT_NUM = true }

-- 数值ID -> 名称
local function __trainer_disaster_name_map()
    local dt = game_world_define and game_world_define.DisasterType
    if not dt then return nil end
    local byId = {}
    for k, v in pairs(dt) do
        if type(v) == "number" and type(k) == "string" then byId[v] = k end
    end
    return byId
end

local function __trainer_classify(name)
    if not name or __SKIP_NAMES[name] then return "skip" end
    if __MANMADE_NAMES[name] then return "manmade" end
    return "natural"
end

-- 收集所有地块的「激活灾害」：直接读 block.m_disasterMgr.m_tbDisasters（键=灾害ID）
local function __trainer_collect_disasters()
    local out = {}
    if not g_blockMgr then return out end
    local blocks = nil
    pcall(function() if g_blockMgr.GetAllBlocks then blocks = g_blockMgr:GetAllBlocks() end end)
    if type(blocks) ~= "table" then
        local b = nil
        pcall(function() b = g_blockMgr:GetBlock(block_define and block_define.CAMP_ID or 1) end)
        if b then blocks = {b} end
    end
    local byId = __trainer_disaster_name_map() or {}
    for _, block in pairs(blocks or {}) do
        local dm = nil
        pcall(function() dm = block.m_disasterMgr end)
        if type(dm) == "table" and type(dm.m_tbDisasters) == "table" then
            for tid, dis in pairs(dm.m_tbDisasters) do
                local active = false
                pcall(function() active = dis:IsActive() end)
                if active then
                    local name = byId[tid] or ("ID_" .. tostring(tid))
                    out[#out + 1] = {block = block, id = tid, name = name,
                                     classify = __trainer_classify(name), disaster = dis}
                end
            end
        end
    end
    return out
end
"""

LUA_DISASTER_PROBE = LUA_DISASTER_TYPES + r"""
local ok, err = pcall(function()
    local lines = {"=== 灾害探查 ==="}
    local dt = game_world_define and game_world_define.DisasterType
    if not dt then return "[失败] game_world_define.DisasterType 不存在（请先进入游戏场景）" end
    local list = {}
    for k, v in pairs(dt) do
        if type(v) == "number" and type(k) == "string" then list[#list + 1] = k .. "=" .. tostring(v) end
    end
    table.sort(list)
    table.insert(lines, "DisasterType: " .. table.concat(list, ", "))
    local found = __trainer_collect_disasters()
    table.insert(lines, "激活灾害数 = " .. tostring(#found))
    local n = 0
    for _, d in ipairs(found) do
        n = n + 1
        if n <= 20 then
            table.insert(lines, "  [" .. d.classify .. "] " .. tostring(d.name) .. " id=" .. tostring(d.id))
        end
    end
    if #found == 0 then
        table.insert(lines, "（当前没有进行中的灾害）")
    end
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_DISASTER_CLEAR = LUA_DISASTER_TYPES + r"""
local ok, err = pcall(function()
    local want = "__WANT__"
    local found = __trainer_collect_disasters()
    local closed, failed = 0, 0
    for _, d in ipairs(found) do
        if want == "all" or d.classify == want then
            local okc = pcall(function() d.disaster:SetActive(false) end)
            pcall(function() if d.disaster.UnInit then d.disaster:UnInit() end end)
            if okc then closed = closed + 1 else failed = failed + 1 end
        end
    end
    local label = (want == "natural") and "天灾" or ((want == "manmade") and "人祸" or "灾害")
    return "[成功] 已关闭 " .. tostring(closed) .. " 处" .. label
        .. "（激活灾害共 " .. tostring(#found) .. "，失败 " .. tostring(failed) .. "）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


def probe_disaster():
    """灾害探查（游戏内进行中的灾害）"""
    return execute_lua_safe(LUA_DISASTER_PROBE, timeout=8.0)


def clear_natural_disaster():
    """零天灾：关闭进行中的自然灾害（水災/地震/饥荒/乾旱/寒潮…）"""
    log("正在清除天灾 ...")
    code = LUA_DISASTER_CLEAR.replace("__WANT__", "natural")
    success, result = execute_lua_safe(code, timeout=10.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"零天灾失败: {result}")
    return success, result


def clear_manmade_disaster():
    """零人祸：关闭进行中的人祸（流民/叛乱/犯罪…）"""
    log("正在清除人祸 ...")
    code = LUA_DISASTER_CLEAR.replace("__WANT__", "manmade")
    success, result = execute_lua_safe(code, timeout=10.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"零人祸失败: {result}")
    return success, result


# ============================================================
# 9. 税收（自动纳税）
# ============================================================
# 游戏机制（源码 pak_lua_dump/sim_common/script/gameplay/tax/tax_mgr.lua）：
#   g_TaxManager:OnDay() 监听 NEW_DAY，CheckTimeToPay(year,month,day) = (year>1 and month==1 and day==1)
#     -> SendTaxPage()：g_LHBUIProvider:EmitTo("LBlockProvider", S2UI_SendPayTax, data) 弹出「纳税」面板
#     -> 玩家点确认 -> LBlockProvider:UI2S_ConfirmPayTax() -> g_TaxManager:PayForTax()
# 用户诉求：不想手动点、也不想跳过（仍要照缴）-> 把 SendTaxPage 换成直接 PayForTax（不弹窗、不弹对话）

LUA_TAX_PROBE = r"""
local ok, err = pcall(function()
    local lines = {"=== 税收状态 ==="}
    local tm = g_TaxManager
    if not tm then
        table.insert(lines, "[失败] g_TaxManager 不存在（请先进入游戏场景）")
        return table.concat(lines, "\n")
    end
    table.insert(lines, "自动纳税已挂钩 = " .. tostring(_G.g_trainer_orig_tax_SendTaxPage ~= nil))
    table.insert(lines, "taxCount（累计缴税） = " .. tostring(tm.taxCount))
    table.insert(lines, "curPaytax（上次缴税） = " .. tostring(tm.curPaytax))
    table.insert(lines, "sendHistory（已弹过提示对话） = " .. tostring(tm.sendHistory))
    if tm.DumpTaxInfo then
        local ok2, info = pcall(function() return tm:DumpTaxInfo() end)
        if ok2 and type(info) == "table" then
            table.insert(lines, "当前品阶 boomLevel = " .. tostring(info.boomLevel))
            table.insert(lines, "税率 taxFactor = " .. tostring(info.taxFactor))
            table.insert(lines, "当前金钱 curMoney = " .. tostring(info.curMoney))
            table.insert(lines, "按现值预计缴税 tax = " .. tostring(info.tax))
        end
    end
    table.insert(lines, "缴税时点 = 每年 1 月 1 日（year > 1）")
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_TAX_AUTO_ENABLE = r"""
local ok, err = pcall(function()
    local tm = g_TaxManager
    if not tm then return "[失败] g_TaxManager 不存在（请先进入游戏场景）" end
    if not tm.SendTaxPage then return "[失败] g_TaxManager:SendTaxPage 不存在" end
    if not _G.g_trainer_orig_tax_SendTaxPage then
        _G.g_trainer_orig_tax_SendTaxPage = tm.SendTaxPage
    end
    -- [FIX 2026-09-14] 自动纳税：跳过纳税面板与提示对话，直接扣款
    tm.SendTaxPage = function(self)
        if self.PayForTax then
            local ok2, e2 = pcall(function() self:PayForTax() end)
            if not ok2 then
                return "[自动纳税] PayForTax 异常: " .. tostring(e2)
            end
        end
        return 1
    end
    return "[成功] 已开启自动纳税（不再弹「纳税」面板，改为自动扣款；累计缴税仍正常累加）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_TAX_AUTO_DISABLE = r"""
local ok, err = pcall(function()
    local tm = g_TaxManager
    if not tm then return "[失败] g_TaxManager 不存在" end
    if _G.g_trainer_orig_tax_SendTaxPage then
        tm.SendTaxPage = _G.g_trainer_orig_tax_SendTaxPage
        _G.g_trainer_orig_tax_SendTaxPage = nil
        return "[成功] 已恢复原版纳税弹窗"
    end
    return "[提示] 当前未开启自动纳税，无需恢复"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""

LUA_TAX_PAY_NOW = r"""
local ok, err = pcall(function()
    local tm = g_TaxManager
    if not tm then return "[失败] g_TaxManager 不存在（请先进入游戏场景）" end
    if not tm.PayForTax then return "[失败] g_TaxManager:PayForTax 不存在" end
    tm:PayForTax()
    return "[成功] 已按当前税率缴纳一次（累计缴税 = " .. tostring(tm.taxCount) .. "）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


def probe_tax():
    """税收状态探查（诊断用）"""
    return execute_lua_safe(LUA_TAX_PROBE, timeout=8.0)


def enable_auto_tax():
    """开启自动纳税：跳过弹窗/对话，直接扣款"""
    log("正在开启自动纳税 ...")
    success, result = execute_lua_safe(LUA_TAX_AUTO_ENABLE, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"自动纳税开启失败: {result}")
    return success, result


def disable_auto_tax():
    """恢复原版纳税弹窗"""
    log("正在恢复原版纳税弹窗 ...")
    success, result = execute_lua_safe(LUA_TAX_AUTO_DISABLE, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"自动纳税恢复失败: {result}")
    return success, result


def pay_tax_now():
    """立即按当前税率缴纳一次"""
    log("正在手动缴纳一次税款 ...")
    success, result = execute_lua_safe(LUA_TAX_PAY_NOW, timeout=8.0)
    if success and isinstance(result, str) and result.startswith("[成功]"):
        log_success(result)
    else:
        log_error(f"缴税失败: {result}")
    return success, result
