# 平野孤鸿项目交接文档

> 交接日期：2026-09-12
> 主项目目录：`D:\pingye_pack\daizuoproject\`
> 游戏：平野孤鸿 (Ballads of Hongye)，Steam AppID 2656540

---

## 一、项目概述

本项目是针对西山居城建经营游戏《平野孤鸿》的逆向工程与修改器开发项目。经历了从MOD系统计划书→逆向工程(7阶段)→创造模式工具→统一修改器v0.1→v0.3多轮bug修复→GUI代码重构→存档编辑器独立的完整演进。

**当前有两个可交付产物：**
1. **woldvein_trainer v0.3** — 全能游戏修改器（左侧导航 + 6 个页面，DLL注入+Lua执行）
2. **save_editor_tool v1.0** — 独立存档编辑器（存档管理+内容编辑）

---

## 二、目录结构速查

```
D:\pingye_pack\
├── daizuoproject\               # 【主项目目录】
│   ├── woldvein_trainer\        # 【主力项目】修改器 v0.3
│   │   ├── main.py              # 入口
│   │   ├── 启动修改器.bat        # 推荐启动方式
│   │   ├── dist\                # 编译产物（EXE+DLL）
│   │   ├── src\                 # 源码（gui已拆分为Mixin）
│   │   └── docs\                # PRD+用户手册
│   ├── yuanma\                  # 源码副本1（同步用）
│   ├── yuanma02\                # 源码副本2（用户指定）
│   ├── CHANGELOG.md             # 完整变更日志
│   ├── AGENTS.md                # 项目总览（技术事实+死路清单）
│   └── HANDOVER.md              # 本文档
│
├── releases\
│   ├── save_editor_tool\        # 【独立工具】存档编辑器 v1.0
│   │   ├── dist\save_editor_v1.0.exe
│   │   └── src\
│   └── v1.0.0\                  # 旧版MOD加载器
│
├── knowledge\Tear-it-all-down\  # 【知识库】逆向工程成果（719类/13110方法）
│   ├── 整合文档_20260909\       # 各类系统深度拆解文档
│   ├── pak_lua_dump\            # 1760个Lua原始脚本
│   └── lua_binding_authoritative.json  # 权威绑定清单
│
├── creative_mode_v1.0\          # 散文件版创造模式（6个Lua+安装bat）
├── development\                 # 历史项目（v1.1 Agent、eastfamily C#）
├── docs\                        # 通用文档
├── assets\                      # 资源备份
├── tools\                       # 工具脚本
└── backups\                     # 源码备份
```

---

## 三、修改器 (woldvein_trainer) 详解

### 3.1 左侧导航 + 6 个页面

| 标签页 | 功能 | 源码文件 |
|---|---|---|
| 资源修改 | 9种资源+幸福度+知名度，实时显示当前值 | `src/gui/tab_resource.py` |
| 创造模式 | 鸿业满级/全建筑解锁/无限资源/升级无限制 | `src/gui/tab_creative.py` + `src/creative_mode.py` + `src/lua_engine.py` |
| 游戏监控 | 进程/内存/日志/崩溃检测 | `src/gui/tab_monitor.py` + `src/game_monitor.py` |
| 高级工具 | NPC/时间天气/建造升级/SimWorld | `src/gui/tab_advanced.py` + `src/advanced_tools.py` |
| 世界系统 | 市场物价/产业链/流民灾害/知名度/建筑精细 | `src/gui/tab_world.py` + `src/world_tools.py` |
| 应用设置 | 诊断日志/日志管理/散文件MOD管理/热键配置入口 | `src/gui/tab_settings.py` |

> 存档编辑已独立为 `save_editor_tool`；热键设置已独立为 `hotkey_configurator.py`（独立工具，非标签页）。

### 3.2 GUI架构（Mixin模式）

`main_gui.py`（436行）定义主类 `TrainerApp`，继承6个Mixin：
```python
class TrainerApp(ResourceTabMixin, CreativeTabMixin, HotkeyTabMixin,
                 MonitorTabMixin, AdvancedTabMixin, SettingsTabMixin):
```
- 主类负责：`__init__`、窗口设置、样式、顶部栏、日志面板、托盘、进程检测、DLL注入、main函数
- 每个标签页由一个Mixin构建（`tab_hotkey.py` 现仅承接热键回调，不再构建标签页）
- 所有 `self.xxx` 属性和方法跨Mixin共享，不要重命名

### 3.3 核心技术链路

```
用户点击按钮
  → Python层调用 execute_lua(code)
    → 生成请求ID（8位UUID）
    → 写入 %LOCALAPPDATA%\woldvein_trainer\lua_cmd.txt
       格式：REQ_ID:xxxxxxxx\n + Lua代码
    → 轮询 lua_result.txt（超时5秒，校验请求ID）
  → DLL层（注入到游戏进程）
    → my_lua_pcall hook 每帧检查命令文件
    → 解析请求ID → 读取Lua代码 → lua_loadstring → lua_pcall执行
    → 结果写入 lua_result.txt（第一行带相同请求ID）
  → Python层校验请求ID匹配 → 解析结果 → 更新GUI
```

### 3.4 竞态 Bug 与防护（v0.3.0 修复）

**问题**：两个 tab 各有 3 秒定时刷新，A 请求超时释放锁 → B 立即写入 → DLL 刚写完 A 的结果 → B 读到 A 的结果串号。

**双重防护**：
1. **GameStatusProvider 单例**（`src/game_status.py`）：所有状态刷新共享同一次 Lua 查询，有订阅者才启动，从根源消除并发
2. **请求 ID 机制**：每次调用带 8 位 UUID，DLL 回写时带回，Python 端校验不匹配则跳过（兜底防护）

### 3.5 关键全局变量名（极易出错）

| 功能 | 正确变量名 | 错误写法（已踩坑） |
|---|---|---|
| 时间管理器 | `g_Time` | `g_TimeManager` |
| 天赋管理器 | `g_TalentManager` | — |
| NPC管理器 | `g_CityManager.m_lActiveCity.m_lCityNpcMgr` | `g_LCityNpcManager` |
| BuildingMgr | `_G.g_BuildingWorldModule.BuildingMgr` | `_G.LBuildingMgr` |
| 建筑卡片 | `g_LBuildingCardManager.tabBuildingCards` | — |
| UI事件 | `g_LHBUIProvider:EmitTo("LSystemProvider", event, data)` | `g_LHBUI:Emit()` |

### 3.6 运行方式

**推荐（源码模式）：**
```
双击 D:\pingye_pack\daizuoproject\woldvein_trainer\启动修改器.bat
```
BAT会自动检查Python环境、安装依赖、启动修改器。

**打包EXE：**
```
D:\pingye_pack\daizuoproject\woldvein_trainer\dist\woldvein_trainer_v0.3.exe
```
注意：EXE可能不是最新代码，修改源码后需重新打包。

**手动运行：**
```bash
cd D:\pingye_pack\daizuoproject\woldvein_trainer
pip install psutil keyboard pystray pillow
python main.py
```

### 3.7 构建命令

**编译DLL：**
```bash
cd D:\pingye_pack\daizuoproject\woldvein_trainer
D:\TOOL\mingw64\mingw64\bin\gcc.exe -shared -O2 -Wall -m64 -o dist\woldvein_trainer.dll src\injector\trainer.c -lpsapi
```

**打包EXE：**
```bash
cd D:\pingye_pack\daizuoproject\woldvein_trainer
pyinstaller --onedir --windowed --name "woldvein_trainer_v0.3" `
  --add-data "dist\woldvein_trainer.dll;dist" `
  --add-data "docs;docs" `
  --collect-all keyboard --collect-all pystray --collect-all PIL `
  --hidden-import psutil --hidden-import src.* --hidden-import src.gui.* `
  main.py
```

---

## 四、存档编辑器 (save_editor_tool) 详解

### 4.1 功能
- 存档管理：扫描存档、中文重命名、UUID恢复、index同步、备份清理
- 存档编辑：.boh解密、userdata表JSON编辑、保存回加密格式
- 深色主题GUI，游戏路径可配置

### 4.2 运行
```
D:\pingye_pack\releases\save_editor_tool\dist\save_editor_v1.0.exe
```

### 4.3 存档格式
- `.boh` = SQLite数据库
- `userdata`表：`path` + `buffer`
- `buffer`加密：ROR3 + 每16字节反转
- 解密：每16字节反转 + ROL3

---

## 五、知识库使用指南

### 5.1 快速查API

**权威绑定清单：**
```
D:\pingye_pack\knowledge\Tear-it-all-down\lua_binding_authoritative.json
```
719类/13110方法，搜索类名或方法名即可。

**整合文档（按系统分类）：**
```
D:\pingye_pack\knowledge\Tear-it-all-down\整合文档_20260909\
```
重点文档：
- `75_时间管理器_LTimeManager.md` — 时间/速度/季节API
- `151_建筑提供器系统_LBuildingProvider.md`
- `168_建筑卡牌管理器系统_LBuildingCardManager.md`
- `89_建筑卡牌系统_LBuildingCard.md`

**原始Lua脚本：**
```
D:\pingye_pack\knowledge\Tear-it-all-down\pak_lua_dump\sim_common\script\
```
搜索游戏实际实现时直接grep。

### 5.2 查API的正确姿势
1. 先在 `lua_binding_authoritative.json` 搜方法名
2. 再在 `整合文档_20260909\` 找对应系统的深度拆解
3. 最后在 `pak_lua_dump\` 搜实际Lua实现，确认参数和返回值

---

## 六、已知问题与待办

### 6.1 待解决（按优先级）

| 优先级 | 问题 | 说明 |
|---|---|---|
| P1 | EXE需重新打包 | v0.3.0 多处改动（竞态修复/UI布局/JSON转义/DLL更新），dist中的EXE还是旧版 |
| P1 | 创造模式建筑解锁不完整 | 三层突破方案反而破坏，已回退到卡片hook+天赋检查hook。需在游戏运行时用Lua命令探测实际解锁状态 |
| P2 | 时间加速/季节变换待验证 | 已修复为g_Time:SetTimeSpeed/SetSeason，用户尚未验证 |
| P2 | pystray未安装 | 系统托盘功能降级，不影响主功能。`pip install pystray pillow` |

### 6.2 已验证死路（不要再尝试）

- `_G.LBuildingMgr` 不存在
- lua_call/lua_settable inline hook → 0xC0000005崩溃
- 直启游戏EXE → XGSDK code=1000黑屏
- `SetUnlockState(false)` 隐藏低等级建筑 → 实际是锁定，与全解锁冲突
- `g_TimeManager` 全局变量名不存在（实际是 `g_Time`）
- `g_LBuildingProvider` 不是全局变量（通过 `g_LHBUIProvider:EmitTo` 通信）
- `UpMaxAllTalent()` 调用可能触发状态重置反而锁定建筑
- `sys._MEIPASS` 作为DLL通信路径 → 重启修改器后功能全废
- `psutil.memory_maps()` 在Windows上枚举模块不可靠
- **多 tab 并发定时刷新 + 文件锁超时 → 竞态串号** → 用 GameStatusProvider 单例 + 请求ID 双重防护

### 6.3 常见问题排查

**Q: 修改器启动报错 `No module named 'src.gui.tab_xxx'`**
A: 检查 `src/__init__.py` 和 `src/gui/__init__.py` 是否存在（空文件即可）。

**Q: DLL注入成功但Lua执行超时**
A: 1) 确认已进入游戏存档（g_camp未就绪时部分命令超时）；2) 检查 `%LOCALAPPDATA%\woldvein_trainer\` 下是否有lua_cmd.txt；3) 旧DLL可能驻留游戏进程，关闭游戏后重开。

**Q: 热键不生效**
A: 必须以**管理员身份**运行修改器。日志中会有警告提示。

**Q: 资源修改显示"未进入场景"**
A: 必须进入游戏存档（不是主菜单），g_camp才会初始化。

**Q: 创造模式开启后建筑还是锁的**
A: 这是已知待解决问题。当前方案只hook了卡片方法，天赋系统的解锁可能需要其他方式。

---

## 七、数据文件位置

| 类型 | 路径 |
|---|---|
| 配置文件 | `%LOCALAPPDATA%\woldvein_trainer\config.json` |
| 日志文件 | `%LOCALAPPDATA%\woldvein_trainer\logs\trainer_YYYYMMDD.log` |
| 备份目录 | `%LOCALAPPDATA%\woldvein_trainer\backups\` |
| DLL通信 | `%LOCALAPPDATA%\woldvein_trainer\lua_cmd.txt` / `lua_result.txt` |
| 游戏存档 | `D:\steam\steamapps\common\BalladsOfHongye_CN\userdata\` |
| 散文件MOD | `D:\steam\steamapps\common\BalladsOfHongye_CN\sim_common\` |

---

## 八、源码同步流程

修改 `daizuoproject\woldvein_trainer` 源码后，需同步到两个备份目录：

```powershell
$src = "D:\pingye_pack\daizuoproject\woldvein_trainer"
foreach ($dst in @("D:\pingye_pack\daizuoproject\yuanma", "D:\pingye_pack\daizuoproject\yuanma02")) {
    if (Test-Path "$dst\src") { Remove-Item "$dst\src" -Recurse -Force }
    Copy-Item "$src\src" "$dst\src" -Recurse -Force
    Copy-Item "$src\main.py" "$dst\main.py" -Force
}
```

**注意：必须先删除旧src再复制，否则旧文件会残留。**

---

## 九、关键文件索引

| 文件 | 作用 | 行数 |
|---|---|---|
| `src/lua_engine.py` | Lua脚本模板 + execute_lua（请求ID竞态防护） | 核心 |
| `src/game_status.py` | 统一状态刷新Provider（单例+订阅，消除并发） | 新增 |
| `src/injector/trainer.c` | DLL源码（inline-hook lua_pcall + 请求ID解析） | ~540 |
| `src/creative_mode.py` | 创造模式开关逻辑 | — |
| `src/advanced_tools.py` | 高级工具Lua脚本 | — |
| `src/gui/main_gui.py` | GUI主类 + 样式系统 | ~500 |
| `src/gui/tab_*.py` | 各标签页Mixin（卡片式布局） | 150-400 |
| `src/gui/diagnostic_panel.py` | 通用诊断面板组件 | — |
| `src/logger.py` | 日志系统（含clear_log_file） | — |
| `src/config.py` | 配置管理 | — |
| `src/hotkey_manager.py` | 全局热键 | — |
| `src/game_monitor.py` | 游戏监控 | — |
| `src/resource_editor.py` | 资源修改 | — |
| `src/injector/__init__.py` | DLL注入核心 | — |

---

## 十、变更日志

完整变更历史见 `CHANGELOG.md`。

**近期重大变更：**
- 2026-09-12（v0.3.0）：竞态Bug修复（GameStatusProvider单例 + 请求ID机制）、JSON转义修复、UI卡片式布局重构、DLL重新编译
- 2026-09-12：时间控制修复（g_Time+SetTimeSpeed）、GUI拆分Mixin、存档编辑器独立、散文件MOD管理
- 2026-09-11：v0.3发布（全源码注释）、八轮bug修复（P0键名不一致、通信路径_MEIPASS、opcode 0x81等）
- 2026-09-10：逆向工程7阶段完成
- 2026-09-09：MOD系统计划书、创造模式工具初版

---

*本文档最后更新：2026-09-12 (v0.3.0)*
