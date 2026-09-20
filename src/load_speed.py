#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
woldvein Trainer v0.4.1 - 读档加速模块（进存档进度条很慢）

【问题】
    进入存档（读档）时，进度条有时候非常慢，能拖几十秒。

【原理：为什么慢 —— 从游戏 Lua 源码里挖出来的】
    读档 = 引擎加载场景资源 + Lua 反序列化存档对象。慢的是第二部分，因为游戏
    故意把「反序列化」分帧执行（为了不让加载卡死）：

      1) script/core/serialization/serialization_mgr.lua:331
             if ((nil == bMain and nil ~= co) or (false == bMain))
                and nTickCount > game_world_define.SERIALIZE_COUNT_PER_TICK then
                 nTickCount = 0
                 coroutine.yield(false, nCount, idx)      -- 每 120 个对象就让出一次

      2) script/gameplay/gameworld/game_world.lua:1039
             LoadArchiveTask.co_LoadArchive = coroutine.create(g_ArchiveMgr.LoadArchive)
             function LoadArchiveTask:OnTick(dt)
                 coroutine.resume(self.co_LoadArchive, g_ArchiveMgr, arUUID)  -- 每帧只 resume 一次
             end

      → 结论：读档需要的帧数 ≈ 存档对象总数 / 120。
        中后期存档轻松上万个对象 → 上百帧；而加载界面期间游戏本身帧率就很低，
        于是「上百帧」被拉成几十秒。这就是进度条慢的根源。
      3) 另外 game_world_define.LOAD_SCRIPT_COUNT_PER_TICK = 20，每帧只 import 20 个脚本。
      4) 进度条显示的还不是真实进度：LScene:TryToCalculateFakeSceneLoadingProgress 里
         有个「假的 spline 进度」，每帧只加 0.3 * (6000/5*0.016) / nSplineTotalCheckCount，
         所以进度条在视觉上是一点点往前挪的（就算加载马上就好）。

【本模块做什么（全部可一键还原，不改游戏文件）】
    1) 抬高 SERIALIZE_COUNT_PER_TICK（每帧反序列化对象上限）
         · 加速档：2400  （约 20 倍，帧数减少 20 倍，仍有分帧、不卡顿）
         · 极致档：10 亿（一次性读完，等于关掉分帧；单帧内做完，可能一瞬间卡一下）
    2) 抬高 LOAD_SCRIPT_COUNT_PER_TICK（每帧 import 脚本数）：20 → 200 / 100000
    3) 勾住 LSerializationMgr:Unserialize —— 每次读档前把上面两个常量重设一次。
       （game_world_define 会在场景卸载时被 unload 再重建，只设一次只对「本次」生效）
    4) 进度条假进度直通：LScene:TryToCalculateFakeSceneLoadingProgress 直接返回 1.0
       （UI 侧 LCommonProvider:S2UI_OnGameLoading 会把 >0.7 的都夹成 0.7，所以只是视觉到位）
    5) 引擎侧 KG3DEngineOption.bAlwaysUpdateLoading = true（加载更新不被前台/渲染状态节流）

【用法】
    DLL 已注入 + 已进入游戏场景 → 点「⚡ 开启加速」或「🚀 极致加速」→ 之后所有读档都生效。
    想恢复：点「↩ 还原」。

【注意】
    - 不改动游戏任何文件；只改运行期内存里的常量和函数。
    - 极致档会在单帧里完成整个反序列化，超大存档可能有 1~2 秒卡顿（加载界面下无感）。
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.lua_engine import execute_lua_retry
from src.logger import log, log_success, log_error, log_warning
from src.constants import LUA_TIMEOUT, LUA_TIMEOUT_LONG


# ============================================================
# Lua：探查当前读档相关状态
# ============================================================
LUA_LOAD_SPEED_PROBE = r"""
local ok, err = pcall(function()
    local lines = {"=== 读档加速 · 状态诊断 ==="}

    local GWD = _G.game_world_define
    if GWD then
        table.insert(lines, string.format("SERIALIZE_COUNT_PER_TICK   = %s    （原版 120：每帧反序列化多少个存档对象）",
            tostring(GWD.SERIALIZE_COUNT_PER_TICK)))
        table.insert(lines, string.format("LOAD_SCRIPT_COUNT_PER_TICK = %s    （原版 20：每帧 import 多少个脚本）",
            tostring(GWD.LOAD_SCRIPT_COUNT_PER_TICK)))
    else
        table.insert(lines, "game_world_define 不存在（还没进关卡/场景）")
    end

    table.insert(lines, string.format("当前加速档 = %s", tostring(_G.g_wt_load_speed_level or "关（原版速度）")))
    table.insert(lines, string.format("Unserialize 已挂钩 = %s", tostring(_G.g_wt_ours_unserialize ~= nil)))
    table.insert(lines, string.format("进度条假进度已直通 = %s", tostring(_G.g_wt_ours_fakeprog ~= nil)))

    -- 估算「按当前设置需要多少帧」
    local okS, tb = pcall(function()
        local st = g_Storage:GetTable(storage_define.root_key.Serialization)
        return st and st.tbObjInfos
    end)
    if okS and type(tb) == "table" and #tb > 0 then
        local n = #tb
        local per = (GWD and tonumber(GWD.SERIALIZE_COUNT_PER_TICK)) or 120
        if per and per > 0 then
            table.insert(lines, string.format("内存中的存档对象 = %d 个 → 按每帧 %d 个 ≈ 需要 %d 帧",
                n, per, math.ceil(n / per)))
        end
    else
        table.insert(lines, "（内存里暂时读不到存档对象表：读档瞬间才有，正常）")
    end

    -- 引擎侧加载选项
    local okO, opt = pcall(function() return g_CoreEngine:GetIEngine():GetKG3DEngineOption() end)
    if okO and opt then
        table.insert(lines, string.format("引擎 bAlwaysUpdateLoading = %s  fForceLoadRadiusInMeter = %s",
            tostring(opt.bAlwaysUpdateLoading), tostring(opt.fForceLoadRadiusInMeter)))
    else
        table.insert(lines, "引擎选项读不到（g_CoreEngine 未就绪）")
    end

    -- 当前场景引擎加载状态
    if g_SceneManager then
        local okSc, sc = pcall(function() return g_SceneManager:GetCurScene() end)
        if okSc and sc and sc.GetCurrentLoadingState then
            local okSt, p, total, fin = pcall(function() return sc:GetCurrentLoadingState() end)
            if okSt then
                table.insert(lines, string.format("当前场景引擎加载状态：progress=%s 任务总数=%s 已完成=%s",
                    tostring(p), tostring(total), tostring(fin)))
            end
        end
    end

    table.insert(lines, "")
    table.insert(lines, "提示：帧数越少读档越快。开「极致档」= 1 帧读完。")
    return table.concat(lines, "\n")
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# Lua：开启读档加速（__MODE__ / __SERIAL__ / __SCRIPT__ 由 Python 注入）
# ============================================================
LUA_LOAD_SPEED_ENABLE = r"""
local ok, err = pcall(function()
    local mode   = "__MODE__"
    local serial = __SERIAL__
    local script = __SCRIPT__

    -- 1) 记住原值（只记一次，方便还原）
    local GWD = _G.game_world_define
    if _G.g_wt_load_orig == nil then
        _G.g_wt_load_orig = {
            SERIALIZE_COUNT_PER_TICK   = (GWD and GWD.SERIALIZE_COUNT_PER_TICK) or 120,
            LOAD_SCRIPT_COUNT_PER_TICK = (GWD and GWD.LOAD_SCRIPT_COUNT_PER_TICK) or 20,
        }
    end
    _G.g_wt_load_speed_level = mode
    _G.g_wt_load_serial      = serial
    _G.g_wt_load_scripts     = script

    -- 2) 把常量写进 game_world_define（读档时会实时读取，所以立刻见效）
    _G.g_wt_load_apply = function()
        local g = _G.game_world_define
        if not g then return false end
        g.SERIALIZE_COUNT_PER_TICK   = _G.g_wt_load_serial
        g.LOAD_SCRIPT_COUNT_PER_TICK = _G.g_wt_load_scripts
        return true
    end
    local appliedNow = _G.g_wt_load_apply()

    -- 3) 勾住 Unserialize：每次读档前重设一次
    --    原因：game_world_define 会在场景卸载时被 UnLoadScript 卸掉、下次再重建（值回到 120/20）
    local mgr = g_SerializationMgr
    if mgr and mgr.Unserialize and _G.g_wt_ours_unserialize == nil then
        _G.g_wt_orig_unserialize = mgr.Unserialize
        local function wt_unserialize(self, ...)
            pcall(_G.g_wt_load_apply)
            return _G.g_wt_orig_unserialize(self, ...)
        end
        _G.g_wt_ours_unserialize = wt_unserialize
        mgr.Unserialize = wt_unserialize
        -- 类表也换一份：存档管理器重建实例后依然生效
        local mt = getmetatable(mgr)
        if type(mt) == "table" and type(mt.__index) == "table" then
            mt.__index.Unserialize = wt_unserialize
        end
    end

    -- 4) 进度条假进度：直接返回 1.0（UI 侧会夹到 0.7），不再一点点爬
    if _G.LScene and _G.LScene.TryToCalculateFakeSceneLoadingProgress and _G.g_wt_ours_fakeprog == nil then
        _G.g_wt_orig_fakeprog = _G.LScene.TryToCalculateFakeSceneLoadingProgress
        local function wt_fakeprog(self, data) return 1.0 end
        _G.g_wt_ours_fakeprog = wt_fakeprog
        _G.LScene.TryToCalculateFakeSceneLoadingProgress = wt_fakeprog
        local mt2 = getmetatable(_G.LScene)
        if type(mt2) == "table" and type(mt2.__index) == "table" then
            mt2.__index.TryToCalculateFakeSceneLoadingProgress = wt_fakeprog
        end
    end

    -- 5) 引擎侧：加载更新不被「窗口后台/不渲染」节流
    local okE, opt = pcall(function() return g_CoreEngine:GetIEngine():GetKG3DEngineOption() end)
    if okE and opt then
        if _G.g_wt_load_orig_bAlwaysUpdateLoading == nil then
            _G.g_wt_load_orig_bAlwaysUpdateLoading = opt.bAlwaysUpdateLoading
        end
        pcall(function() opt.bAlwaysUpdateLoading = true end)
    end

    local orig = _G.g_wt_load_orig
    return string.format(
        "[成功] 读档加速已开启（%s）：每帧反序列化 %s→%s、脚本导入 %s→%s；进度条假进度已直通；引擎 bAlwaysUpdateLoading=true。"
        .. "立刻生效=%s；因为勾住了 Unserialize，以后每次读档都会自动重设，不用重复点。",
        mode,
        tostring(orig.SERIALIZE_COUNT_PER_TICK), tostring(serial),
        tostring(orig.LOAD_SCRIPT_COUNT_PER_TICK), tostring(script),
        tostring(appliedNow))
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# ============================================================
# Lua：还原（常量 / Hook / 引擎选项 全部复原）
# ============================================================
LUA_LOAD_SPEED_DISABLE = r"""
local ok, err = pcall(function()
    local orig = _G.g_wt_load_orig

    -- 1) 常量还原
    if orig and _G.game_world_define then
        _G.game_world_define.SERIALIZE_COUNT_PER_TICK   = orig.SERIALIZE_COUNT_PER_TICK or 120
        _G.game_world_define.LOAD_SCRIPT_COUNT_PER_TICK = orig.LOAD_SCRIPT_COUNT_PER_TICK or 20
    end

    -- 2) Unserialize 还原（实例 + 类表）
    local mgr = g_SerializationMgr
    if mgr and _G.g_wt_orig_unserialize then
        mgr.Unserialize = _G.g_wt_orig_unserialize
        local mt = getmetatable(mgr)
        if type(mt) == "table" and type(mt.__index) == "table" then
            mt.__index.Unserialize = _G.g_wt_orig_unserialize
        end
    end

    -- 3) 假进度还原（类表 + 实例方法表）
    if _G.LScene and _G.g_wt_orig_fakeprog then
        _G.LScene.TryToCalculateFakeSceneLoadingProgress = _G.g_wt_orig_fakeprog
        local mt2 = getmetatable(_G.LScene)
        if type(mt2) == "table" and type(mt2.__index) == "table" then
            mt2.__index.TryToCalculateFakeSceneLoadingProgress = _G.g_wt_orig_fakeprog
        end
    end

    -- 4) 引擎选项还原
    if _G.g_wt_load_orig_bAlwaysUpdateLoading ~= nil then
        local okE, opt = pcall(function() return g_CoreEngine:GetIEngine():GetKG3DEngineOption() end)
        if okE and opt then
            pcall(function() opt.bAlwaysUpdateLoading = _G.g_wt_load_orig_bAlwaysUpdateLoading end)
        end
    end

    -- 5) 清理全局标记
    _G.g_wt_load_speed_level = nil
    _G.g_wt_load_serial      = nil
    _G.g_wt_load_scripts     = nil
    _G.g_wt_load_apply       = nil
    _G.g_wt_ours_unserialize = nil
    _G.g_wt_ours_fakeprog    = nil
    _G.g_wt_load_orig_bAlwaysUpdateLoading = nil
    return "[成功] 读档加速已还原（常量 / Unserialize Hook / 假进度 / 引擎选项 全部恢复原版）"
end)
if not ok then return "[错误] " .. tostring(err) end
return err
"""


# 加速档参数：mode -> (SERIALIZE_COUNT_PER_TICK, LOAD_SCRIPT_COUNT_PER_TICK)
SPEED_LEVELS = {
    "fast":  ("加速档", 2400, 200),          # 约 20 倍：帧数大幅减少，仍有分帧，最稳
    "turbo": ("极致档", 1000000000, 100000),  # 一次性读完：等价关掉分帧，可能单帧小卡顿
}


def _log_result(success, result, fail_msg):
    """统一按返回值前缀分级打日志（沿用项目里其他模块的约定）"""
    if success and isinstance(result, str):
        if result.startswith("[成功]"):
            log_success(result)
        elif result.startswith("[警告]") or result.startswith("[提示]"):
            log_warning(result)
        else:
            log_error(result)
    else:
        log_error(f"{fail_msg}: {result}")
    return success, result


def probe_load_speed():
    """探查读档相关状态（常量、Hook、估算帧数）"""
    return execute_lua_retry(LUA_LOAD_SPEED_PROBE, timeout=LUA_TIMEOUT, attempts=2, tag="读档诊断")


def enable_load_speed(mode="fast"):
    """开启读档加速。mode: fast=加速档(约20倍) / turbo=极致档(一次性读完)"""
    level, serial, scripts = SPEED_LEVELS.get(mode, SPEED_LEVELS["fast"])
    log(f"正在开启读档加速（{level}）...")
    code = (LUA_LOAD_SPEED_ENABLE
            .replace("__MODE__", level)
            .replace("__SERIAL__", str(serial))
            .replace("__SCRIPT__", str(scripts)))
    success, result = execute_lua_retry(code, timeout=LUA_TIMEOUT_LONG, attempts=3, tag="读档加速")
    return _log_result(success, result, "读档加速开启失败")


def enable_load_speed_fast():
    """开启读档加速（加速档，推荐先用这个）"""
    return enable_load_speed("fast")


def enable_load_speed_turbo():
    """开启读档加速（极致档：一次性读完，最猛）"""
    return enable_load_speed("turbo")


def disable_load_speed():
    """还原读档加速（全部恢复原版）"""
    log("正在还原读档加速 ...")
    success, result = execute_lua_retry(LUA_LOAD_SPEED_DISABLE, timeout=LUA_TIMEOUT_LONG,
                                        attempts=3, tag="读档加速还原")
    return _log_result(success, result, "读档加速还原失败")
