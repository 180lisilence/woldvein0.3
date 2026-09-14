# woldvein_trainer - 平野孤鸿全能修改器 v0.3

> 最后更新：2026-09-12
> 状态：活跃开发
> 技术栈：Python 3.14 + tkinter + C DLL (mingw-w64) + pystray

## 项目定位

整合所有功能的统一游戏修改器，对标 Cheat Engine / WeMod，纯内存操作，不修改游戏磁盘文件。

## 目录结构

```
woldvein_trainer\
├── main.py                      # 入口
├── 启动修改器.bat                # BAT启动脚本（纯英文，避免中文编码问题）
├── hotkey_configurator.py       # 独立热键配置工具
├── 热键配置.bat                  # 启动热键配置工具
├── config.json                  # 运行时配置（自动生成）
├── dist\
│   └── woldvein_trainer.dll     # 注入DLL（59KB，inline-hook lua_pcall + 请求ID竞态防护）
│   └── woldvein_trainer_v0.3.exe # 打包主程序（onedir 目录模式）
├── docs\
│   ├── PRD_v0.1.md              # 产品需求文档
│   └── 用户手册.md
├── src\
│   ├── __init__.py              # 包标识（相对导入必需）
│   ├── config.py                # 配置管理（深合并，LOCALAPPDATA路径）
│   ├── logger.py                # 日志系统（多线程加锁，含clear_log_file）
│   ├── lua_engine.py            # Lua执行引擎+脚本模板（请求ID竞态防护）
│   ├── game_status.py           # 统一游戏状态提供者（单例+订阅模式，消除并发刷新）
│   ├── resource_editor.py       # 资源修改
│   ├── creative_mode.py         # 创造模式（选项可独立开关）
│   ├── hotkey_defs.py           # 热键唯一定义源
│   ├── resource_defs.py         # 资源唯一定义源
│   ├── lua_lib.py               # Lua辅助库（统一UI事件 + hook保存/还原）
│   ├── hotkey_manager.py        # 全局热键管理
│   ├── game_monitor.py          # 游戏监控（进程/内存/日志/崩溃）
│   ├── advanced_tools.py        # 高级工具（NPC/时间天气/建造升级/SimWorld）
│   ├── world_tools.py           # 世界系统（市场/产业链/流民/知名度/建筑精细）
│   ├── _archive\                # 历史代码归档（不再使用）
│   │   └── save_editor_legacy\  # 存档编辑相关（已独立为 save_editor_tool 项目）
│   ├── injector\
│   │   ├── __init__.py          # DLL注入核心（EnumProcessModulesEx，LoadLibraryW Unicode）
│   │   └── trainer.c            # 通用Trainer DLL源码
│   └── gui\
│       ├── __init__.py          # GUI包标识
│       ├── main_gui.py          # GUI主界面（主类+托盘+进程检测+注入）
│       ├── tab_resource.py      # 资源修改标签页Mixin
│       ├── tab_creative.py      # 创造模式标签页Mixin
│       ├── tab_hotkey.py        # 热键回调Mixin（不构建标签页）
│       ├── tab_monitor.py       # 游戏监控标签页Mixin
│       ├── tab_advanced.py      # 高级工具标签页Mixin
│       ├── tab_world.py         # 世界系统标签页Mixin
│       ├── tab_settings.py      # 应用设置标签页Mixin
│       ├── theme.py             # 三主题色板（深简/Bento/墨笺）
│       ├── kpi_bar.py           # 顶部 KPI 数据条（常驻核心数据）
│       ├── scrollable.py        # 侧边滚动条
│       ├── widgets.py           # 控件工厂 + 颜色取用
│       ├── async_helper.py      # 异步执行 + 按钮冷却
│       ├── toast.py             # 轻量通知
│       ├── tooltip.py           # 气泡提示
│       └── diagnostic_panel.py  # 通用诊断面板组件
└── verify.py                    # 验证脚本
```

## 功能模块（左侧导航 + 6 个页面）

1. **资源修改**：10种资源（金钱/木料/矿产/衣物/食物/水/盐/酒/精华/人口，人口不提供一键修改）+幸福度+知名度，实时显示当前值（统一GameStatusProvider刷新）
2. **创造模式**：4个子选项独立开关（鸿业满级/全建筑解锁/无限资源/升级无限制），卡片式布局
3. **游戏监控**：进程/内存/CPU实时监控，Lua错误检测，崩溃自动分析，存档状态，复制错误信息
4. **高级工具**：NPC管理，时间/天气/季节控制，建造升级细粒度控制，SimWorld操作，时间流速实测
5. **世界系统**：市场物价、产业链、流民灾害、灾害控制（零天灾/零人祸）、知名度（双存储）、建筑精细操作、税收（自动纳税）；蓝图/NPC 详情为探查面板
6. **应用设置**：诊断日志输出，日志路径管理，清空日志，散文件MOD安装/卸载，热键配置工具入口

> 注：存档编辑已独立为 `save_editor_tool` 项目；热键设置已独立为 `hotkey_configurator.py`（独立工具，非标签页）。

## 核心技术

### DLL注入
- 方法：OpenProcess + VirtualAllocEx + WriteProcessMemory + CreateRemoteThread(LoadLibraryW)
- ctypes 必须设置 argtypes/restype（64位句柄不截断）
- 路径用 UTF-16-LE + LoadLibraryW（支持中文路径）
- 模块枚举：`EnumProcessModulesEx` + `GetModuleFileNameExW`（不用psutil.memory_maps）

### Trainer DLL
- inline-hook `lua_pcall`（Lua5X64.dll 导出）
- 指令长度：自研 x86-64 解码器（256项 opcode 表 + ModR/M + SIB 解析）
- 关键opcode：`0x81` = `0x07`（imm32=4字节 + ModR/M位）
- 失败时放弃安装，不回退到硬编码长度
- 通信：轮询 `%LOCALAPPDATA%\woldvein_trainer\lua_cmd.txt`，执行后写 `lua_result.txt`
- **竞态防护（请求ID机制）**：命令文件第一行 `REQ_ID:xxxxxxxx`，结果文件第一行带相同ID，Python端校验不匹配则跳过
- **GameStatusProvider**：所有状态刷新共享同一次查询（src/game_status.py），从根源消除并发
- BOM：必须跳过 UTF-8 BOM 头（EF BB BF），否则 loadstring 失败
- 定制 Lua5X64.dll：无 lua_getglobal/lua_setglobal/lua_tostring 导出，用 lua_getfield(L,-10002,name) + lua_tolstring

### 创造模式 Lua 脚本
- 选项变量：`g_cm_opt_max_boom` / `g_cm_opt_unlock_buildings` / `g_cm_opt_infinite_resources` / `g_cm_opt_unlimited_upgrade`
- 鸿业满级：`boom:setBoom(14)` + hook IsSatisfied/GetBoom + UI刷新
- 全建筑解锁：hook SetUnlockState/GetUnlockState + scheme:SetBuildingCardState
- 无限资源：hook ConsumeResource/_ConsumeResource + ModifySourceValue 跳过负值
- 升级无限制：SetFucntionState(ADVANCED_UPGRADE, OPEN) + 遍历 g_functionType 全部设 OPEN
- 单等级建筑保护：hook CheckCanUpgradeBuilding时检查最大等级，最大等级=1不允许升级
- **P0键名**：ENABLE保存 `__cm_orig_CheckCanCreate`/`__cm_orig_CheckCanUpgrade`（无Building后缀），DISABLE必须对齐

### 时间控制（易错）
- 全局对象：`g_Time`（**不是** `g_TimeManager`）
- 时间加速：修改 `g_GameWorld.TICK_DELTA_TIMES`（控制 LogicTick 触发频率，影响日历+建筑+NPC产出）；`g_Time:SetTimeSpeed` 只影响日历，已弃用
- 季节变换：hook `GetCurSeason`/`GetSeason` 返回固定值（直接 `SetSeason` 会被月度重算覆盖）
- 跳过天数：基于 `UpdateSpecialTime` 的跳天逻辑（`months*30` 天），绕开 `SetTimeToMonthsLater` 的 `challengeblock` nil 错误
- **`m_nDayStamp` 是单调累计天数**（`_updateDay` 逐日累加、跨年不重置）；`GetDayStamp()` 在游戏里只被灾害调度用作差值 → 回写必须用「天数增量」，禁止写成 `(月-1)*30+日`
- 原版节奏：`SECONDS_PER_DAY = define.DAY_TICK_COUNT`，`DAY_TIME_REAL` = 原版「1 游戏日 = 多少实时秒」；逻辑 Tick 触发周期 = `g_GameWorld.TICK_DELTA_TIMES`
- 暂停：`g_Game:LogicTickPause()`（停止所有逻辑Tick）；恢复 `g_Game:LogicTickResume()`
- UI事件：`g_LHBUIProvider:EmitTo("LSystemProvider", event, data)`

### 存档格式
- .boh = SQLite 数据库
- userdata 表：path + buffer
- buffer 加密：加密=ROR3 + 每16字节反转；解密=每16字节反转 + ROL3
- .meta 行：明文 JSON（存档名/日期/季节/等级）
- /TRANSLATE_V 行：版本标记

## 构建命令

### 编译 DLL
```bash
D:\TOOL\mingw64\mingw64\bin\gcc.exe -shared -O2 -Wall -m64 -o dist\woldvein_trainer.dll src\injector\trainer.c -lpsapi
```

### 打包 EXE
```bash
pyinstaller --onedir --windowed --name "woldvein_trainer_v0.3" `
  --add-data "dist\woldvein_trainer.dll;dist" `
  --add-data "docs;docs" `
  --collect-all keyboard --collect-all pystray --collect-all PIL `
  --hidden-import psutil --hidden-import src.* --hidden-import src.gui.* `
  main.py
```

### 源码运行
```bash
python main.py
# 或使用BAT
启动修改器.bat
```

## 已知限制

- 全局热键需要**管理员权限**运行
- DLL 注入后关闭修改器，DLL 仍驻留游戏进程（直到游戏退出）
- 创造模式关闭后，部分 UI 可能需要切换场景才完全刷新
- 资源当前值显示依赖 `g_camp.m_tbSource`，未进入场景时显示"未进入场景"
- pystray未安装时系统托盘功能降级（不影响主功能）
- 状态刷新已统一为 GameStatusProvider 单例 + 请求ID双重防护，不再有并发竞态问题

## 源码同步

修改后需同步到两个目录（先删除旧src再复制）：
- `D:\pingye_pack\woldvein_trainer_source_v0.1\`
- `D:\pingye_pack\source_codebaocun\`

## 数据文件位置

- 配置：`%LOCALAPPDATA%\woldvein_trainer\config.json`
- 日志：`%LOCALAPPDATA%\woldvein_trainer\logs\trainer_YYYYMMDD.log`
- DLL通信：`%LOCALAPPDATA%\woldvein_trainer\lua_cmd.txt` / `lua_result.txt`
