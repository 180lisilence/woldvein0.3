# 平野孤鸿项目变更日志

## 2026-09-15

### v0.3.7 - 微信三栏布局全功能版 + 搜索功能

**版本号更新**
- `trainer_ui_tk.py`: VERSION = "v0.3.7"
- `main.py`: 头部注释更新为 v0.3.7
- `src/constants.py`: APP_VERSION = "0.3.7"

**新功能：搜索框真正可用**
- 中间功能列表顶部搜索框从摆设变为真正可用
- 跨所有分类搜索（主页/进程/资源/创造/工具/存档/设置）
- 输入关键词实时过滤，显示匹配的功能项
- 搜索结果带分类标签（── 资源 ──）
- 点击搜索结果直接跳转到对应功能
- 清空搜索框恢复正常列表

**修复：启动方式统一为 main.py**
- `main.py` 改为导入 `trainer_ui_tk` 的 main 函数（原为 `src.gui.main_gui`）
- 启动脚本 `启动修改器_v0.3.6.bat` 改为 `python main.py`
- 单实例互斥体更新为 `woldvein_trainer_mutex_v036`
- 桌面快捷方式「平野孤鸿修改器 v0.3.6」指向 main.py 启动

**修复：全局文字左对齐**
- 主页状态卡片：标题和数值左对齐（原为居中）
- 进程页：进程信息左对齐
- 一键全开页：提示文字和功能清单左对齐
- 存档管理页：存档目录提示、存档列表左对齐
- 热键设置页：提示文字左对齐
- 日志管理页：路径文字左对齐
- MOD管理页：说明文字、状态文字左对齐
- 关于页：版本信息左对齐

---

## 2026-09-15

### v0.3.6 - 微信三栏布局全功能集成版

**UI 重做：微信电脑客户端三栏布局**
- 完全抛弃旧版 tab 标签页布局，改为微信风格三栏结构
- 左侧导航栏（70px，浅灰 #f7f7f7）：图标按钮，选中微信绿 #07C160 高亮
- 中间功能列表（260px，白色）：搜索框 + 功能项（图标+名称+描述+状态红点）
- 右侧操作面板：顶部标题栏（56px）+ 中间滚动操作区 + 底部日志区
- 配色：主色 #07C160（微信绿），正文纯黑 #000000，次要文字 #999999，分割线 #e6e6e6
- 字体：微软雅黑

**功能全部集成（无占位页）**

主页：
- 游戏/DLL/Lua 三个状态卡片（每3秒自动更新）
- 快速操作按钮（启动游戏/注入DLL/检测进程）

进程：
- 检测游戏进程 / 启动游戏 / 注入DLL
- 进程信息显示（PID + DLL状态）

资源修改：
- 8种资源单独增加（可自定义数量，默认100万）
- 一键全部资源 +100万
- 资源归零（带确认对话框）
- 幸福度最大 / 知名度 +10000 / 恢复幸福度

创造模式：
- 4个选项（鸿业满级/全建筑解锁/无限资源/无限制升级）
- 全选/反选
- 开启/关闭创造模式
- 诊断解锁状态

高级工具（12个子功能）：
- ⏰ 时间控制：1x/2x/4x/8x加速、春夏秋冬、跳天跳月、诊断
- 🌤️ 天气控制：固定晴天/恢复天气/诊断
- 👤 NPC管理：探查NPC/谋士升满级/探查谋士/人口满员
- 🏠 建造控制：建筑列表/全部升级/全部完工/升级到顶级
- 🏙️ 城市品阶：品阶+1/满级/完成条件/诊断/城市全发展
- 🎖️ Steam成就：全解锁/地块挑战/探查
- 🌾 地块解锁：全解锁/探查
- 🧠 天赋系统：全解锁/满级/+200点/诊断
- 🌪️ 灾害控制：清除地震/全关闭/禁用触发/自然/人为灾害
- 🎆 节日控制：暂停/关闭烟花/清除广告/固定季节/跳过事件
- 💎 核心数值：金钱/幸福度/创造力/繁荣/品阶直接设置 + 市场/产业链/难民/声望/税收
- 🔥 一键全开：所有作弊一次性开启

存档管理：
- 刷新存档列表
- 备份当前存档（整个存档目录）
- 备份单个存档文件
- 清理旧备份（带确认）

设置：
- ⌨️ 热键设置：12个热键列表 / 恢复默认 / 重新注册
- 📝 日志管理：清空日志文件 / 打开日志目录 / 复制日志路径
- 📦 MOD管理：检测散文件MOD / 安装 / 卸载
- ℹ️ 关于：版本信息

**技术实现**
- 独立界面文件 `trainer_ui_tk.py`（约1000行）
- 所有业务操作通过 `threading.Thread` 异步执行，不卡UI
- 日志通过 `set_log_callback` 实时显示到GUI
- 状态检测每3秒自动刷新

---

## 2026-09-14

### v0.3.4 - 微信三栏布局初版（PyQt5 尝试 → tkinter 实现）

**UI 重做尝试**
- 用户要求按照微信电脑客户端三栏结构重做UI
- 先尝试 PyQt5 + QSplitter 实现
- 发现用户 Python 3.14 不支持 PyQt5/PyQt6（无预编译包）
- 尝试 winget 安装 Python 3.12，被用户制止（"你都不问我吗？"）
- 最终改用 tkinter 实现微信三栏布局

**初版功能**
- 纯界面布局，无业务逻辑
- 左侧导航 + 中间功能列表 + 右侧操作面板
- 主页/进程/资源/创造模式 四个页面有基本界面
- 其他页面为占位

---

## 2026-09-14

### v0.3.1 - 旧版 tab 布局稳定版

**基础功能**
- 7大标签页：资源修改/创造模式/存档编辑/热键设置/游戏监控/高级工具/应用设置
- DLL注入 + inline-hook lua_pcall 执行Lua脚本
- 资源修改（8种资源 + 幸福度 + 知名度）
- 创造模式（鸿业满级/全建筑解锁/无限资源/无限制升级）
- 高级工具（时间/天气/NPC/建造/城市/成就/天赋/灾害等）
- 存档管理
- 热键管理
- 游戏监控

**已知问题**
- UI布局为传统 tab 标签页，视觉效果一般
- 部分高级工具功能失效（时间加速/季节变换/NPC人数状态）
- 创造模式建筑解锁有缺陷

---

## 技术栈

- **语言**：Python 3.14 + tkinter
- **DLL**：C (mingw-w64)，Inline Hook Lua5X64.dll 的 lua_pcall
- **通信**：命令文件（lua_cmd.txt / lua_result.txt）轮询
- **游戏**：平野孤鸿 (Ballads of Hongye)，Steam AppID 2656540
- **游戏路径**：D:\steam\steamapps\common\BalladsOfHongye_CN


---

## v0.3.1 及更早版本详细历史


## 2026-09-14

### 修复：多开修改器把命令通道踩坏（注入/升级「假失败」）+ 任务「直接改数据」解锁/完成

**现象**：面板注入失败；品阶升级等操作也失效。日志里「注入面板」的返回值是**状态轮询的 JSON**（别人的结果）。

**根因（实机确证）**
- 用户同时开了**两个修改器实例**（PID 9212 @21:18、PID 15048 @21:26）。两个进程各自都有后台状态轮询线程，
  都在写同一份 `%LOCALAPPDATA%\woldvein_trainer\lua_cmd.txt`、读同一份 `lua_result.txt`；
- `open(CMD_FILE,"w")` 是「先截断再分片写入」（Python 文本层默认 8KB 缓冲），两进程交叉写 →
  DLL 可能读到「A 的 REQ_ID + B 的代码」这种拼接内容 → 结果串号 → App 判定为失败；
- 请求ID 竞态防护只在「读到不匹配 ID」时跳过，但拼接内容恰好让 ID 匹配，
  于是把别人的 JSON 当成了自己的结果（日志：`[ERROR] {"prosperity_level":...}`）。

**修复**
- `src/lua_engine.py`
  - 命令文件**原子写入**：先写 `.tmp` 再 `os.replace`（同分卷原子），DLL 只会看到完整的旧内容或完整的新内容
  - **跨进程通道锁**（`lua_channel.lock` + msvcrt 文件锁）：`execute_lua` 全程持锁；
    原函数体改名为 `_execute_lua_inner`，`_lock` 由 `Lock` 改 `RLock` 以支持外层包装
  - 新增 `execute_lua_retry(code, timeout, attempts, tag, expect)`：拿不到有效结果、或结果前缀不符（疑似串号）就重发，每次全新请求ID
- `main.py`：**单实例保护**（命名互斥体 `woldvein_trainer_mutex_v03`），已有实例时弹提示并退出
- 关键操作改用重试版本：面板注入/移除（3 次）、品阶逐级晋升（2 次）、激活全部任务（2 次）

**新功能：任务「直接改数据」解锁 / 完成**（按用户要求：不绕游戏内部流程，直接把数据改成满足条件的样子）
- 源码依据（`task.lua:254`）：`LTask:CheckPreConditions()` 第一句就是
  `if self.unlockPre then retBool = true; break; end` —— 这就是游戏自带的 GM 短路分支，
  把 `unlockPre` 写成 true，游戏自己就会判定「前置触发条件已满足」
- **解锁**：`unlockPre=true` + `status=ACTIVATED(2)` + `timeLog` + 分桶 `tbUnStartTasks → tbCurTasks`
- **完成**：`status=FINISHED(4)` + `isNextTaskFinished=true` + 分桶 `→ tbFinishedTasks` + `RecieveReward()` 按配置发奖；
  `CheckPreviousTask()` 读的是「前置任务的 status」，因此置为 FINISHED 后后续任务的前置链判定自然通过
- 高级工具页「任务」区块新增「🔧 改数据解锁」「🔧 改数据完成」；游戏内面板新增「任务」区块
- 新增静态体检脚本 `_tmp_luacheck.py`：剥离注释/字符串后核对全部 Lua 片段的块配对（14 段全部 OK）

### 修复：游戏内面板中文乱码 / 折叠展不开 / 面板一直闪

**用户反馈**：游戏内面板「字体乱、一直刷新、展不开、看不懂」。

**根因（源码级确定）**
- **中文乱码**：注入的 Lua 代码是 **UTF-8**（Python 端 `lua_cmd.txt` 用 utf-8 写入，DLL 原样交给 `luaL_loadstring`），
  而 `util.a2u8` 是 **ANSI/GBK → UTF-8**（游戏自己的 `.lua` 是 GBK 才需要它，见 `ui_base_case.lua:58`
  的 `self.m_strTable[str] or util.a2u8(str)` 带缓存写法）。对已经是 UTF-8 的中文再转一次 = 乱码
- **折叠加不开 + 一直闪**：同一根因的连带效应——对非法输入每帧可能产出不同字节，
  使 `ImGui.CollapsingHeader` 的标签（即控件 ID）每帧变化 → 折叠状态每帧被重置，永远展不开、画面持续刷新

**修复（`src/advanced_tools.py`）**
- **去掉 `util.a2u8`**，字符串 UTF-8 原样直传（文件头写明原因，防止以后又加回去）
- 折叠头统一带 `ImGuiTreeNodeFlags_.ImGuiTreeNodeFlags_DefaultOpen` → **默认展开**，
  即使鼠标点击被游戏抢走也能看见内容；签名不兼容时自动降级 `CollapsingHeader(label)` → `Text`
- **同一 ImGui 帧只画一次**：用 `ImGui.GetFrameCount()` 去重（重复 `Begin/End` 同一窗口会重置折叠状态）
- 窗口标题改 ASCII（`woldvein Trainer vX.Y.Z###wt_panel`），`###` 后的 ID 恒定 → 移动/折叠状态稳定
- `SetNextWindowPos/Size` 用 `ImGuiCond_.ImGuiCond_FirstUseEver`（原来写死数字 4）
- 错误处理：连续 5 帧报错才自动关闭（原为一次报错即卸载）；新增诊断区块
  （`GetIO()` 鼠标坐标 / WantCaptureMouse / IsWindowHovered + 字体直传测试行 + 最近操作与最近错误）
- 面板内「品阶+1（含解锁）」优先调用 Python 侧注册的 `_G.g_trainer_boom_step`（同一套解锁流程），
  fallback 补齐 `BoomLevelChange / UI2S_BoomUpgradeCallback / UpdateHistoryMaxBoomLevel / UpdateBoom / _syncUI`；
  新增「立即缴税」按钮；自动纳税开关复用 Python 侧同一批状态全局（`g_trainer_tax_*`），不再各自为政
- `LUA_BOOM_UPGRADE_STEP` 核心循环抽出为 `_G.g_trainer_boom_step(target)` 供面板复用

### 修复/新增：窗口默认尺寸、蓝图与 NPC 探查、游戏内 ImGui 面板

**1. 窗口默认尺寸（用户反馈「必须最大化才能用全部」）**
- 旧逻辑硬上限 `min(screen*0.8, 1280x800)` → 1080p 屏默认仅 1280x800，内容放不下
- 改为 `min(screen*0.92, 1680x1000)`；已保存尺寸 `< 1400x860` 视为不可用并用默认；`minsize(1020,700)`

**2. 蓝图探查（旧探针找错对象，恒为 0）**
- 旧逻辑扫建筑上的 `IsBlueprint` 标记 → 永远 0
- 真·蓝图系统 = **`g_LBlueprintManager`**（图纸合成）+ 谋士府图纸研发
- 新探针输出：管理器可用方法、逐地块「合成中 / 有可用合成」、谋士府研发状态与成本
- **实机结果**：`地块数=57 合成中总数=0 有可用合成的地块=0`；谋士府研发成本=4900

**3. NPC 探查（旧版只有 id，没有名字）**
- 实测破译：`g_LNPCManager.npcs` 是 133 个 LNPC 对象（键为 userdata）；
  **姓名/性别/年龄在 `npc.tabMateData`（Name/Gender/Age）**；配置表 `NpcRes` 298 条（同为 tabMateData）
- 新探针按 城市NPC管理器 → `g_LNPCManager` → 观光NPC管理器 多来源枚举，并输出 name/gender/age
- **实机结果**：`id=1 name=张圣武 gender=男 age=59 …`

**4. 新功能：游戏内折叠面板（ImGui）**
- **关键发现**：游戏 UI 基于 **Dear ImGui**，Lua 侧直接暴露 `ImGui / KLImGui / ImVec2`；
  `g_LUiPageManager:GameDraw(dt)` 是逐帧绘制入口 → 包装它即可在游戏画面内用 ImGui 画自己的窗口
- 由引擎渲染、**不开外部覆盖窗口**，所以不像旧版「浅层破解」的外部悬浮窗那样卡
- 面板含可折叠区块：状态 / 时间倍速(1x/2x/4x) / 快捷操作（品阶+1含解锁、自动纳税开关）；出错自动卸载
- 高级工具页新增「游戏内面板（ImGui）」区块：注入 / 移除 / 状态
- **实机验证**：GameDraw 逐帧 ≈64fps；`帧计数=15923 最近错误=无`

### 修复：自动纳税失效（改为「钩类」，读档重建实例仍生效）

**用户反馈**：点了「自动纳税」后照旧弹「纳税」窗口。

**根因（实机确证）**
- `tax_mgr.lua` 的 `__onload__` 每次都执行 `_G.g_TaxManager = LTaxManager:new()`——
  **读档 / 切场景 / 重开都会重建实例**；旧实现只替换「实例方法」，换档即失效（新实例又变回原版 → 弹窗复发）
- 该框架的类方法挂在 `getmetatable(g_TaxManager).__index`（类表）上，`_G.LTaxManager` 并非全局

**修复**
- 改为替换**类方法**：`idx.SendTaxPage`（自动缴税，不弹面板/对话）+ `idx.OnDay`
  （保留「到期才缴」判定避免每日误扣；并在其中自愈 SendTaxPage），实例侧同步兜底
- `probe_tax` 增加「类/实例是否已替换」、日期、税率、现值预计缴税

**实机验证**
- 挂钩返回：`自动纳税已挂钩 LTaxManager『类』（读档重建实例仍生效；不弹面板）`
- 状态：类方法表已定位 / 类上 SendTaxPage 已替换 / 类上 OnDay 已替换 / 实例已替换 = 全 true
- 模拟 `g_TaxManager:SendTaxPage()` → `ok=true ret=1，金钱 520000 → 520000`（未弹窗、未扣款、立即返回）

**参考实现分析**（`daizuoproject\3\BalladsOfHongye_Trainer.exe` + `BalladsTrainer.dll`）
- 路线：**DX11 Present 钩子注入自绘 ImGui 覆盖层** + **Lua 引擎钩子**注入 `Trainer.` 脚本
  （DLL 内可见 `lua_pcall`/`lua_getglobal`/`lua_setglobal`/`Trainer.applyInfiniteResources`，
  按名字扫描 Lua 全局、每 tick 重应用的「自适应」思路）
- 功能：无限资源/秒建造/无灾害/繁荣度满/全部开启 + F10 面板；**无纳税功能**
- 借鉴：**每 tick 重应用（自愈）** 已用于本次修复（OnDay 内自愈 SendTaxPage）
- 差异：它用外部 DX11 覆盖层（旧版「浅层破解」卡顿来源）；本修改器改用游戏自带 ImGui（Lua 侧），引擎渲染

### 新功能：城市品阶「逐级晋升（含解锁）」+ 任务激活/完成

**根因**：旧「品阶 +1」只调 `g_camp.boom:setBoom(level)`——**只改数字**，
既不派发 `BoomLevelChange`（工作坊/谋士/风水/声望监听），也不调
`UI2S_BoomUpgradeCallback(level)`（按该级 `Rewards` 解锁 建筑卡/谋士卡/天赋/载具/功能/自定义功能，
并触发剧情）。因此升级奖励与内容解锁被整体跳过——用户反馈「不完整」。

**实机探查（只读，v0.3.1 存档）**
- 品阶 `GetBoom()=2`，`CITY_MAX_LEVEL=14`，`GetBoomLevelCfg` 14 级
- 每级配置字段：`BlockNum/BoomLevel/BoomScore/Conditions/DevelopmentRequirement/Happiness/…/Rewards/ResourceReward/Title/UIRewards`
- 本级 Rewards 21 项、下一级 24 项（前 8 均为 `buildingCard`）
- 任务桶：未开始 54 / 进行中 1 / 已接 0 / 已完成 0（共 55）

**实现**
- `advanced_tools.py`：`boom_upgrade_step(target)` / `boom_upgrade_to_max()`——从当前+1 逐级
  `setBoom` → `BoomLevelChange` → `UI2S_BoomUpgradeCallback` → `UpdateHistoryMaxBoomLevel`，
  最后 `UpdateBoom()/_syncUI()` 刷新；每级 pcall 保护并回报解锁项数
- 任务：`probe_tasks()` / `unlock_all_tasks()`（逐任务 `UnlockPrecondition` 激活）/ `finish_all_tasks()`（`FinishAllTask`）
- **注**：`task_mgr` 并不监听 `BOOM_LEVEL_CHANED`，任务与品阶无自动绑定，故任务单独提供按钮
- GUI（高级工具页）：城市品阶区块改为「⬆ 逐级晋升（含解锁）」「⏩ 晋升到顶级」；新增「任务（解锁 / 完成）」区块

**验证**：`compileall` / `verify.py` 全过；实机自检——晋升脚本以 target≤当前 走校验分支（**零改动**）
返回提示；任务探查返回 `54/1/0/0` 与 55 条任务名。

**待实机确认**：点「逐级晋升」后品阶 +1 且该级解锁项（建筑卡等）真的出现；
`UI2S_BoomUpgradeCallback` 在个别奖励分支（依赖当前选中区块 / office）是否报错。

### v0.3.1 发布

**版本**：`0.3.1`（新增唯一版本源 `APP_VERSION`，见 `src/constants.py`；
窗口标题 / 版本标签 / 启动日志 / 「关于」与诊断均由它生成）

**本版内容**
- 新增：**自动纳税**（世界系统页「税收」卡片，跳过每年 1/1 的确认面板直接扣款）
- 新增：**时间流速实测**（高级工具页「📏 实测倍率」，5 点线性回归，避开整数步进量化误差）
- 修复：`m_nDayStamp` 累计语义（跳天/跳月/季节同步）、探查去 cjson 改纯文本、
  `g_TimeDefine`、人口口径（`GetPopulation(tbPSource)` 无参返回 0）、NPC 列表多来源探测
- 回档：撤销融合版三主题 / KPI 数据条 / 圆角 UI（用户反馈不好看），恢复深/浅双主题界面

**产物**
- `dist\woldvein_trainer_v0.3.1\woldvein_trainer_v0.3.1.exe`（PyInstaller onedir）
- `woldvein_trainer_v0.3.1_setup.exe`（Inno Setup 安装包，含卸载 `unins000.exe`）

**构建**
```
python -m PyInstaller --noconfirm woldvein_trainer_v0.3.1.spec
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_build\setup.iss
```

**验证**：源码 `compileall` / `verify.py` 全过；GUI 冒烟 `BUILD OK`（标题 `v0.3.1`）；
PyInstaller 与 ISCC 均成功；打包产物含 `_internal\dist\woldvein_trainer.dll` 与 `docs\`。

### 回档：撤销融合版 UI（三主题 / KPI 数据条 / 圆角）

**原因**：用户认为该 UI 不好看，要求回档。仅回退 UI，功能修复保留。

**回退内容**
- 恢复到 `2e43762` 的界面实现：`theme.py`（深/浅双主题）、`main_gui.py`（单按钮切换、无 KPI 条）、
  `config.py`、`lua_engine.py`（去掉为 KPI 新增的状态字段）、`tooltip.py`、
  `tab_resource.py` / `tab_creative.py` / `tab_monitor.py` / `diagnostic_panel.py`
- 删除新增组件 `src/gui/kpi_bar.py`、`src/gui/rounded.py`
- `tab_advanced.py` / `tab_world.py` / `tab_settings.py`：圆角按钮回退 `ttk.Button`、
  折叠面板容器回退 `tk.Frame`、移除 `.rounded` 导入
- 文档（README / AGENTS / 用户手册 / PRD）主题与目录树描述回退
- 运行配置 `theme` 回滚为 `dark`（本项目 `config.json` 曾为 `bento`）

**保留（功能修复，未回退）**
- 自动纳税（世界系统页「税收」卡片）、实测倍率（高级工具页，5 点回归）
- `m_nDayStamp` 累计语义修复、探查纯文本（去 cjson）、`g_TimeDefine`、人口口径、NPC 列表多来源
- 一键全量探查清单补齐（世界-税收 / 高级-时间流速实测）

**验证**：`compileall` / `verify.py` 全过；GUI 冒烟 BUILD OK、`theme=dark`、无 `kpi_bar`、深浅切换正常、
税收卡片与实测处理函数仍在；截图确认恢复原始深色外观。

### 修复：人口口径 / 实测倍率精度 / g_TimeDefine（实机验证）

**来源**：2026-09-14 全量探查报告 + 直连 Lua 通道复测。

1. **人口口径错误**：`LBaseBlock:GetPopulation(tbPSource)` 必须带参数（人口类型数组），
   无参会直接 `return 0` 并打 Traceback；旧探针 `camp:GetPopulation()` 因此恒为 0。
   修复：改读资源档 `SOURCE.CURRENT_POPULATION(7)`；上限 = `MAX_POPULATION(8) + MAX_REFUGEE_POPULATION(14)`；
   另附 `GetDemilitarizedPopulation()`。
   **实机复测**：population 170 / pop_max 170 / demilitarized 170（原为 0）。
2. **实测倍率量化误差**：原「两点采样」在 4x 下只得 3.66x（m_nCurTime 按整数步进）。
   改为 **5 点线性回归求斜率**。
   **实机复测**：5 点 / 4.26s 窗口 → 实测等效倍率 **4.00x**（与 TICK_DELTA_TIMES 0.625 推导一致）。
3. **`高级-时间系统` 报「TimeDefine 不存在」**：实际全局是 `g_TimeDefine`。
   修复后正确显示 `MIN_TIME_SPEED=1 / MAX_TIME_SPEED=50 / SECONDS_PER_DAY=2`。
4. **`基础-NPC列表` 报「CityNpcManager 不存在」**：改多来源探测后**实机复测成功**：
   `NPC总数: 133 来源=LNPCManager`（本存档无活跃城市，故回退到全局 `g_LNPCManager.npcs`）。
5. 「一键全量探查」清单补齐：新增 `世界-税收`、`高级-时间流速实测`。

**顺带印证**：`m_nDayStamp=2516` 恰等于 `(7-1)×360+(12-1)×30+26` → 累计语义再次确认。

**涉及文件**：`src/advanced_tools.py`、`src/gui/tab_settings.py`

### UI：真圆角（Canvas 绘制）+ 全局按钮 / 卡片接入

**背景**：融合版方案承诺「小半径圆角」，但 tkinter / ttk 的 Frame、Button 原生是直角，
此前只用「描边 + 分层色」近似，实机看仍是直角。

**实现**
- 新增 `src/gui/rounded.py`：
  - `RoundedFrame`：外层仍为普通 `tk.Frame`（尺寸由内容决定，不改变原布局语义），
    圆角背景由一层 `place(relwidth/relheight=1)` 的 Canvas 绘制并置于底层；
  - `RoundedButton`：Canvas 绘制的圆角按钮，API 对齐 `ttk.Button` 常用子集
    （`text/state/style/command/width`、`configure/cget/invoke`、hover 与禁用态、`cursor=hand2`）；
  - `redraw_all()`：主题切换后重绘全部圆角组件（Canvas 不受 ttk 样式影响）。
- 全局接入：**99 处 `ttk.Button` → `RoundedButton`**
  （main_gui 5 / tab_advanced 44 / tab_world 24 / tab_settings 12 / tab_resource 8 / tab_creative 3 / tab_monitor 2 / diagnostic_panel 1）
- `tab_advanced._create_collapsible`：折叠面板容器改 `RoundedFrame`（所有区块卡片圆角）
- `kpi_bar`：KPI 卡片改 `RoundedFrame`
- `tooltip.py`：`bind` 改 `add="+"`，避免覆盖圆角按钮的 hover 绑定

**验证**：`compileall` / `verify.py` 通过；GUI 冒烟（构建 + 三主题切换 + 按钮 `config/cget/state`）通过；
**实机截图**确认三主题下按钮、KPI 卡片、区块卡片均为圆角（像素采样核对 KPI 两行均铺满宽度）。

**已知限制**：真阴影 / 毛玻璃 tkinter 无法实现，仍以「描边 + 分层色」近似。

### UI：融合版三主题（深简 / Bento / 墨笺）+ 顶部 KPI 数据条

**背景**：用户选定「A 骨架 + B 顶部 KPI + C 作为可切主题」的融合方案（一套布局代码，三套主题只换配色）。

**实现**
- `src/gui/theme.py` 重写：`THEMES` 由「深/浅」改为三主题字典 `{shenjian, bento, mojian}`；
  新增 `THEME_ORDER` / `THEME_LABELS` / `next_theme()`；新增 `ThemeChip(.Active).TButton`、`KpiKey/KpiValue.TLabel` 样式。
  - 深简（默认）：`#0F172A` 深板岩 + `#22C55E` 绿强调（瑞士极简骨架）
  - Bento：`#020617` 近黑 + 绿强调（数据密集）
  - 墨笺：`#F3EDE1` 米纸 + `#9E2B22` 朱红（E-Ink 优化，降低白底刺眼；`fg_muted #5C5449` 仍达标）
- 新增 `src/gui/kpi_bar.py`：顶部常驻 KPI 条（金钱/人口/人口上限/木料/矿产/游戏天数/倍速），
  复用 `GameStatusProvider` 单例（不新增轮询）；支持动态着色（人口接近上限→黄、金钱/木料/矿产为 0→红）。
- `main_gui.py`：顶部「深/浅」单按钮 → 三主题芯片；新增 `set_theme()`（`toggle_theme()` 保留为循环切换）；
  内容区顶部接入 KPI 条。
- `lua_engine.LUA_GET_STATUS` 扩展字段：`day_stamp / year / month / tick_delta / speed_mult / pop_max`。
- `config.py`：`theme` 默认 `"shenjian"`。

**验证**：`py_compile` / `compileall` / `verify.py` 全过；GUI 冒烟（构建 + 三主题切换 + KPI 更新）`SMOKE_RC 0`。

### 修复：日志挖出的两个真 bug（g_TimeDefine / NPC 管理器路径）

**来源**：2026-09-14 18:39 全量探查报告（实机）。
1. `高级-时间系统` 恒报「TimeDefine 不存在」——实际全局是 **`g_TimeDefine`**（`time_define.lua` 定义）。
   修复：诊断脚本改用 `g_TimeDefine or TimeDefine`。
2. `基础-NPC列表` 恒报「CityNpcManager 不存在」——报告确认 `g_CityManager:GetActiveCity()` 返回 **nil**
   （对象上只有 `m_lsCityInfo`，无 `m_lActiveCity`）。
   修复：`_LUA_NPC_MGR_HEAD` 改「`GetActiveCity()` 优先 + 旧字段兜底」并回报诊断；
   `LUA_NPC_LIST` 改为**多来源探测**（城市NPC管理器 → `g_LNPCManager.npcs` → `g_LSightSeeingNPCMgr.tbRoles`），
   输出可读文本并注明来源。

**同批报告的实机印证**
- `m_nDayStamp = 556`，恰等于 `(2-1)×360+(7-1)×30+16` → 累计语义确证，与当日修复一致
- 实测倍率：1x → 1.22x，4x → 3.66x（TICK_DELTA_TIMES 0.625）→ 时间倍速 v3 确实生效
- 探查输出已无 `cjson不可用`

**涉及文件**：`src/gui/theme.py`、`src/gui/kpi_bar.py`(新)、`src/gui/main_gui.py`、`src/config.py`、`src/lua_engine.py`、`src/advanced_tools.py`

### 新功能：自动纳税（世界系统）+ 时间流速实测（高级工具）

**背景**：游戏每年正月初一由 `g_TaxManager` 弹「确认纳税」面板，必须手动点确认。用户诉求：照缴但不想点、也不能跳。

**源码定性（`pak_lua_dump/.../gameplay/tax/tax_mgr.lua`）**
- `LTaxManager:OnDay()`（监听 `NEW_DAY`）→ `CheckTimeToPay(y,m,d) = (year>1 and month==1 and day==1)`
- → `SendTaxPage()`：`g_LHBUIProvider:EmitTo("LBlockProvider", S2UI_SendPayTax, data)` 弹出面板
- → 玩家点确认 → `LBlockProvider:UI2S_ConfirmPayTax()` → `g_TaxManager:PayForTax()`

**实现（自动纳税）**
- `world_tools.py`：新增 `LUA_TAX_PROBE / LUA_TAX_AUTO_ENABLE / LUA_TAX_AUTO_DISABLE / LUA_TAX_PAY_NOW`
  与 `probe_tax / enable_auto_tax / disable_auto_tax / pay_tax_now`。
  自动纳税 = 把 `g_TaxManager.SendTaxPage` 换成直接 `PayForTax()`（不弹窗、不弹对话，累计缴税照常累加）。
- `tab_world.py`：新增「税收（自动纳税）」卡片（探查 / 自动纳税 / 恢复弹窗 / 立即缴税一次）。

**时间流速实测（高级工具页「📏 实测倍率」）**
- 源码事实（`time_define.lua`）：`SECONDS_PER_DAY = define.DAY_TICK_COUNT`，
  `TICK_DELTA_TIMES = define.DAY_TIME_REAL / define.DAY_TICK_COUNT`
  → **原版 1 游戏日 = DAY_TIME_REAL 实时秒**；逻辑 Tick 触发周期即 `g_GameWorld.TICK_DELTA_TIMES`。
- `advanced_tools.measure_time_speed()`：连续两次读 `g_Time:GetCurTime()`，用
  「模拟时间差 / 实时时间差」直接测出实际倍率（`≈ DAY_TIME_REAL / 实测实时秒每游戏日`），不依赖假设。

**验证**：`py_compile` / `compileall` / `verify.py` 全项通过。

**涉及文件**：`src/world_tools.py`、`src/advanced_tools.py`、`src/gui/tab_world.py`、`src/gui/tab_advanced.py`

**待实机确认**：开启自动纳税后跨年（1 月 1 日）不再弹面板、金钱正常扣除且「税收探查」taxCount 增加；
「实测倍率」在 1x/2x/4x 下应分别读数约 1/2/4。

### 修复：m_nDayStamp 语义误用（跳天/跳月/季节同步会破坏灾害计时）

**源码定性（`pak_lua_clean\LTimeManager.lua`）**
- `LTimeManager:_updateDay()`：`self.m_tb.m_nDayStamp = self.m_tb.m_nDayStamp + nPastDay`
  → **逐日累加、跨年不重置**，即**单调累计天数**。
- `LTimeManager:GetDayStamp()` 返回该值；全项目检索，它**只被灾害调度用作差值**：
  - `LBaseDisaster:DisasterReliefEvent`：`g_Time:GetDayStamp() - self.m_nProbTime < IntervalDay`
  - `LFloodDisaster` / `LSevereFrostDisaster` / `LColdWinterDisaster` / `LSpringRainGainDisaster`：
    `GetDayStamp() - m_nLastTriggerDay >= CONTINUE_DAYS` / `== RELIEVE_EVENT_DAY` / `< INTERVAL`
  → 一旦回写成“年内值” `(月-1)*30+日`，差值会突变为负 →
  **进行中的灾害永不结束、后续灾害被长时间压制**。

**修复**
- `_LUA_CALENDAR`（跳天/跳月共用）：新值改为**天数增量** `newStamp = curStamp + days`
  （原先写 `(newMonth-1)*30+newDay`）。
- `LUA_TIME_SET_SEASON`（季节同步日期）：不再直接写 `(月-1)*30+日`，改为按**日序差值**累加
  `m_nDayStamp = m_nDayStamp + (newDoy - oldDoy)`，保持单调。
- 顺带修正 `_LUA_CALENDAR` 顶部与代码相矛盾的注释（注释认定不能用年内值，代码此前却用了）。

**验证**：`py_compile` / `compileall` / `verify.py` 全项通过（10 资源 / 12 热键 / DLL 59153 B）。

### 探查输出：去掉 cjson 依赖，改纯文本（游戏 Lua 环境无 cjson）

**现象**：NPC 列表 / 时间状态 / 人口状态 / 建筑列表 / SimWorld 状态 5 个探查脚本走
`pcall(require,"cjson")`，环境缺 cjson 时整段详情退化成字符串 `"cjson不可用"`。

**修复**：新增共享 Lua 片段 `_LUA_TB2TEXT`（`__tb2text(tb)`：数组逐行、字典按 key 排序逐行），
5 个脚本改为 `_LUA_TB2TEXT + (...)` 前置，序列化处改调 `__tb2text(...)`，彻底移除 cjson 依赖。

**涉及文件**：`src/advanced_tools.py`

**待实机确认**：跳天/跳月后 `GetDayStamp` 仍单调递增；探查面板显示完整列表而非 `cjson不可用`。

### 修复：创造模式按钮点击无反应（防呆置灰逻辑漏洞）

**现象**：实机点击「▶ 开启创造模式」完全无反应，日志里也没有任何 `正在开启创造模式...` 记录。

**根因**：`src/gui/main_gui.py`
- `update_modify_buttons_state()` 用 `enabled = self.dll_injected and self._dll_verified`
  统一置灰资源/创造按钮；
- 但 `_dll_verified` 只在 `on_detect_game()` 的「修改器后打开、DLL 已驻留」分支里被置 True；
- 正常路径（点「注入DLL」→ `on_inject_dll()` → `_wait_dll_ready()`）**从不置位**，
  于是 `creative_btn`（属性名恰好匹配）被永久 `DISABLED` → Tk 不派发 command → “点了没反应”。
- 资源页 `resource_buttons` 同样被置灰，实机是靠**全局热键**绕过的，所以此前未被察觉。

**修复**（备份：`_backup_dllbtn_20260914\main_gui.py`）
1. `_wait_dll_ready()` / `_wait_dll_ready_silent()`：Hook 验证通过后置 `_dll_verified = True`
   并刷新按钮状态；Hook 超时/未就绪则置回 `False`，按钮保持灰色（避免再次“点了没反应”）。
2. `on_detect_game()`：把 `_dll_verified = True` 提到 `update_modify_buttons_state()` 之前，
   消除“检测到 DLL 驻留后按钮还要多等 5 秒才可用”的窗口。

**验证**：`py_compile` 通过；`python main.py` GUI 冒烟启动正常。

### 成就模块修复：解锁 Steam 最后两个（月落峡 超甲通关 / 三金牌通关）

**背景**：用户 Steam 里一直差两个成就：`月落峡超甲通关`、`月落峡三金牌通关`。

**源码定位（GBK 解码游戏 Lua 后发现）**
- `月落峡` = 地块 **9**（`block_define.BLOCK_STRATEGIC_PASS_CONFIG[9]`、`LBattleLogic[9]`）
- `achievement_define.lua`：
  - `BLOCK_FINISHED_ACHIEVEMENT[9] = 100`（通关）
  - `BLOCK_BESTSCORE_ACH[9] = 101`（注释即“地块**超甲**通关”）
  - `BLOCK_SPEED_ACH[9] = 102`（“地块速度通关”）
  - `block_define.SCORE_LEVEL`：评分 >110 = **超甲**
- `achievement_mgr.lua`：
  - `BestScore(blockId)` → `UnlockAchievement(BLOCK_BESTSCORE_ACH[blockId])`
  - `BestSpeed(blockId)` → **要求挑战评级 3 项全金（rank==1）**才解锁 = “三金牌”
  - `UnlockAchievement(achId)` 守卫：`if (not unlockState[achId] or direct) and achId then`
    → 内部调 `g_LXGAgentManager:UnlockAchievement(achId)`（C++ 绑定 → XGSDK → Steam）

**两个真 bug（导致这两个成就永远解锁不了）**
1. 旧 `LUA_STEAM_ACHIEVEMENT_UNLOCK_ALL` 用 `cm:GetGDPLById(achId)` 过滤；
   100/101/102 **没有成就卡映射** → 直接进 `missing` 分支被跳过（日志“存在成就ID 81 个”即此）。
2. 旧脚本先 `mgr.unlockState[achId] = true` 再调 `mgr:UnlockAchievement(achId)`；
   而后者有 `if (not unlockState[achId] or direct)` 守卫 → **被自己设置的标志跳过**。
   （`GM_UnlockAllAchievement` 也只循环 `1..99`，同样漏掉 100-102。）

**修复**
- `LUA_STEAM_ACHIEVEMENT_UNLOCK_ALL` 重写：从 **`mgr.config`**（achieve.txt 权威表）+ 地块挑战表
  + 卡片映射取并集获得 achId；直接调 `g_LXGAgentManager:UnlockAchievement(id)`
  并用**返回布尔**判定是否真被平台接受。（`LUA_TIMEOUT+30s`）
- 新增 `LUA_UNLOCK_BLOCK_CHALLENGE_ACH` + `unlock_block_challenge_achievements()`：
  定点解锁地块 9 的 100/101/102，并顺带走一遍游戏自身入口 `BestScore/BlockMerged/BestSpeed`。
- GUI：高级页 →「Steam 成就」新增按钮 **「🎯 月落峡挑战成就」**。

**验证**：`py_compile` / `compileall` / `verify.py` 全项通过；31 模块导入成功。
备份：`_backup_achievement_20260914/`。

**待实机确认**：点按钮后日志应显示 `地块9 挑战成就：推送 N/3`；再到 Steam 查两个成就是否点亮。

### 代码治理：消除硬编码与重复代码（重构）

**新增单一职责模块**
- `src/constants.py`：集中游戏安装路径 / Steam AppID / 鸿业上限 / 成就扫描上限 / 时间权威值 / 执行超时等常量。

**硬编码路径收敛（3 个文件 → 1 处）**
- `config.py` / `game_monitor.py` / `gui/tab_settings.py` 改为引用 `constants.DEFAULT_GAME_PATH`。

**Lua 重复片段抽取为共享常量**（括号内为消除的重复份数）
| 片段 | 消除重复 | 用于 |
|---|---|---|
| `_LUA_TM_HEAD` + `_LUA_CALENDAR` | ×2 | 跳天 / 跳月（历法推算）|
| `_LUA_BUILDINGMGR_HEAD` | ×3 | 建筑列表 / 升级全部 / 立即完成 |
| `_LUA_NPC_MGR_HEAD` | ×3 | NPC 列表 / 添加 / 移除 |
| `_LUA_TIME_BASE_RESOLVE` | ×2 | 设置倍速 / 恢复原速 |
| `_LUA_BOOM_RESOLVE` | ×2 | 品阶+1 / 读取当前品阶 |

**Python 侧去重**
- `_log_result()`：统一 15 处“结果 → 分级日志 + 返回”样板
- `_boom_lua()`：鸿业上限以占位符 `__BOOM_MAX__` 注入 Lua，模板与常量解耦

**GUI 字体去重**
- `theme.py` 新增 `FONT_TITLE/SUB/BOLD/BODY/TINY/MONO_LG/MONO_BOLD/MONO` 8 个常量，
  替换 13 个文件共 **89 处** 重复字体元组。

**魔数常量化**
- `BOOM_MAX_LEVEL`(14) / `ACHIEVEMENT_ID_SCAN_LIMIT`(400) / `LUA_TIMEOUT`(+`_LONG`)
  / `RESOURCE_ADD_AMOUNT`(1_000_000) / `FAME_ADD_AMOUNT`(10_000)

**度量（重构前 → 后）**
- 重复代码块（≥6 行）：**91 → 48 组**
- 硬编码绝对路径：3 文件 → 仅 `constants.py` 单点
- 校验：`py_compile` / `compileall` / `verify.py` 全项通过；**31 个模块全部导入成功**；
  6 个重建的 Lua 常量与备份逐一比对——5 个字节级完全一致，1 个仅多一行 Lua 注释。

**已知剩余（未强改，均为探针/惯例量）**
- 8 处“方法枚举”Lua 片段（`for k,v in pairs(obj) do if type(v)=="function"`）：
  `advanced_tools.py` ×6、`lua_lib.py` ×1、`world_tools.py` ×1
- 建筑 GDP 三重循环 ×3（`for g = 0, 10 do`）
- 惯例量：`1024`(KB/MB)、`3600`(秒→时)、GUI 布局 padding、动画步长

**备份**：`_backup_refactor_20260914/`

### 全量 API 审计：找出并修复所有“猜错/不存在”的游戏接口（12 处）

**做法**：把修改器 58 个内嵌 Lua 脚本里对游戏的全部调用（全局对象 / 对象:方法）自动抽取出来，
对照游戏源码（pak_lua_clean + pak_lua_dump + pak_lua_memory_dump，共 6578 个 lua）建立的
API 索引（1212 个类 / 297 个全局对象）逐个验证。

**审计结论（修复前）**：
- 方法名在游戏“任何类”都不存在（凭空捏造/拼错）：**4 个**
- 在已知对象上调用了该对象没有的方法（对象/方法不匹配）：**6 组**
- 引用了游戏不存在的全局对象：**27 个**（多数为探查脚本的候选名尝试，或修改器自建标志）

**已修复的 12 处**
| # | 原调用（错） | 改为（游戏真实 API） | 位置 |
|---|---|---|---|
| 1 | `g_FunctionManager:GetFucntionState(id)` | `CheckFuncIsUnlock(id)` | LUA_CREATIVE_ENABLE |
| 2 | `g_blockMgr:GetCampBlockId()` | `GetCampBlock():GetBlockID()` | LUA_CREATIVE_ENABLE |
| 3 | `g_GameWorld:IsPaused()` | `g_Game:IsPaused()` | LUA_SIMWORLD_STATUS / TIME_DIAGNOSE |
| 4 | `g_GameWorld:GetFrameCount()` | `g_BuildingWorldModule.BuildingMgr:GetFrameTotalCount()` | LUA_SIMWORLD_STATUS |
| 5 | `g_GameWorld:GetName()` | 移除（LGameWorld 无此方法） | LUA_SIMWORLD_STATUS |
| 6 | `g_GameWorld:RefreshSeason()` | `g_GameWorld.GameWorldAudio:OnNewSeason(season)` | LUA_TIME_SET_SEASON |
| 7 | `boom:getBoom()` | `boom:GetBoom()` | LUA_BOOM_LEVEL_UP / BOOM_GET_CURRENT（3 处） |
| 8 | `camp:GetMoney()` | `camp:GetSourceValue(block_define.SOURCE.MONEY)` | LUA_POPULATION_STATUS |
| 9 | `camp:UpdatePopulation()` | `g_LPopulationManager:_forceAllocatePopulation()` | LUA_RESOURCE_RECALC |
| 10 | 谋士候选名 `g_AdvisorManager`/`g_AdviserManager` | `g_LFamousAdviserMgr` / `g_LAdviserManager` | LUA_ADVISOR_PROBE / MAX_ALL |

**修复后重审**：严重问题 **0**；可解析调用匹配 **101 处**；剩余 24 个“不存在的全局”均为
探查脚本候选名或修改器自建标志（无害）。

**验证**：py_compile OK；`verify.py` 全项通过。备份：`_backup_api_fix_20260914/`。
审计报告：`docs/API审计报告_20260914.md`。

**涉及文件**：`src/advanced_tools.py`、`src/lua_engine.py`

### 三个「假解锁」修复：城市品阶 / 地块 / 产业链（实机反馈：只改 UI、内部没变）

共同病因：调用的游戏接口只改了“显示值/开关”，没有执行游戏自己的解锁流程。

**1）城市品阶（`LUA_COMPLETE_CITY_RANK`）**
- 旧实现直接 `setHistoryMaxBoomLevel(14)` → 游戏 `UpdateHistoryMaxBoomLevel` 的解锁循环是
  `for i = GetHistoryMaxBoom()+1, GetBoom() do UnLockBoomReward(i) end`，**循环为空**；
  结果只有数字/任务系统条件判定变了（“任务UI完成”），
  建筑卡/谋士卡/天赋/载具/功能/地块扩张/灾害解锁等奖励一个都没执行。
- 现改为：`historyMaxBoomLevel=0` → `setBoom(maxLevel)` → `UpdateHistoryMaxBoomLevel()` → 刷新 UI。

**2）地块（`LUA_PLOT_UNLOCK_ALL`）**
- 旧实现乱设 `block.m_nState=2 / state / unlocked / active` 等字段，与游戏枚举不匹配
  （只改了表象）。
- 游戏内部“已拥有”判定为 `m_nState == block_define.STATE.COMBINED / WORKING`
  （`LBlockMgr:GetAllOwnedBlocks`）。现改为 `block:SetState(block_define.STATE.COMBINED)`，
  仅转“未激活”地块，不破坏营地/工作态；并触发 `UpdateFinishedPeaceBlock` + UI 刷新。

**3）产业链（`LUA_CHAIN_UNLOCK_ALL`）**
- 旧实现 `ch:SetUnlockState(true)` 是**空操作**：`bUnlock` 在 ctor 里默认已经是 true。
- 现改为在类方法层覆盖 `_GetbActivedRelation` 恒返回 true（让所有产业链加成生效；
  因 `CalBuildingChainActived` 会重算 `m_tbActiveChainList`，只改数据会被覆盖），
  并把当前所有地块的激活表填满。

**验证**：py_compile OK；`verify.py` 全项通过。备份：`_backup_fix3_20260914/`。

**涉及文件**：`src/advanced_tools.py`、`src/world_tools.py`

### 探查结果乱码修复：结果解码由“整段回退”改为“逐行解码”（实机报告暴露）

**现象**：`probe_report.txt` 的 NPC 段部分中文变成乱码，例如 `=== NPC/鍩庡競绠＄悊鍣ㄦ帰鏌`（应为“NPC/城市管理器探查”）、`缁戝畾鏂规硶`（应为“绑定方法”）；而同一段里来自游戏的数据（如 `Name = 情缘山庄`）却是正常的。

**根因**：一份结果里混杂两种编码——**我们写入的 Lua 字面量是 UTF-8**，**游戏返回的字符串是 GBK**。`lua_engine.py` 原先“整段先试 utf-8，失败就整段按 gbk 解码”，一旦遇到 GBK 字节就整段误判，把我们正常的 UTF-8 字面量也解成了乱码（“城市管理器”按 GBK 解 → “鍩庡競绠”）。

**修复**：改为**逐行解码**——每行先试 UTF-8，该行失败才回退 GBK。两种编码各行其是，互不影响。

**验证**：py_compile OK；构造“UTF-8 字面量 + GBK 游戏数据”混合样本复现并确认修复；`verify.py` 全项通过。

**涉及文件**：`src/lua_engine.py`

### 跳月修复：Lua `string.format` 占位符/参数不配平（实机日志暴露）

**现象**：实机日志 `[ERROR] 跳过月数失败: [string "..."]:41: bad argument #9 to 'format' (number expected, got no value)`（跳 1/3 个月必失败；跳天正常）。

**根因**：`LUA_TIME_SKIP_MONTHS` 的返回格式串有 **8 个 `%%d` 占位符**，却只传了 **7 个参数**——漏传 `months`。对比 `LUA_TIME_SKIP_DAYS`（7 占位符 / 7 参数）可看出差异。

**修复**：`string.format(..., months, days, curYear, curMonth, curDay, newYear, newMonth, newDay)`（补回 `months`）。

**验证**：py_compile OK；`verify.py` 全项通过；全文件 70 处 `string.format` 占位符/参数扫描 0 处失配。

**涉及文件**：`src/advanced_tools.py`

### 时间倍速 v3：修掉“越点越快”的滚雪球（用户反馈“特别特别快”）

**根因**：v2 里我加了“若当前值 ≠ 上次写入值 → 认为游戏改过速度 → 重取基准”。
但**游戏自己会把 TICK_DELTA_TIMES 改小**（或旧的 0.016 写完残留）→ 被当成新基准 → `base/speed` 在错误基准上继续除 → **越点越快（滚雪球）**。

**修复**
- **彻底删除“用当前值当基准”的逻辑**：基准只认游戏权威值 `define.DAY_TIME_REAL / define.DAY_TICK_COUNT`（=2.5）
- 安全钳制：计算出 `newDelta < 0.05` 或 `> 60` 时 **直接中止并提示**，不写入
- `restore` 同样只写权威值，不再依赖内存快照
- 状态面板新增告警：记录基准与权威值不一致时提示“可能已被错误基准污染 → 点恢复速度”

**恢复方法**：重启修改器 → 点「↩ 恢复速度」（写入 2.5）。

**验证**：py_compile OK；4 项自检全 True

**涉及文件**：`src/advanced_tools.py`

### 成就 v2：找到真正推 Steam 的通道（关键修复）

**症结**
- 游戏 Lua 里 **没有** `function *:UnlockAchievement` 的定义 → 它是 **C++ 绑定（tolua）**，内部调 XGSDK/Steam（`LBaseBlock.lua:2133` 注释佐证：`UnlockAchievement calls XGSDK C function`）
- 而之前只调了 `g_LAchieveCardManager:UnlockAchieveCard(g,d,p,l)`（只解锁**图鉴卡**）+ 置 `unlockState[id]=true` → **从未推送平台** → Steam 不亮（这就是“两个都没成功”的原因）

**修复**
- 对每个存在的成就 ID **强制调 `mgr:UnlockAchievement(achId)`**（C++→Steam），且**不因 `unlockState` 已 true 而跳过**（之前正是被跳过）
- 扫描上限 300 → **400**；返回 `推送平台 N 次（UnlockAchievement=True/False，上限 400）` + 失败明细
- 探针新增：`UnlockAchievement 绑定 = function/nil`

**验证**：py_compile OK；4 项自检全 True

**涉及文件**：`src/advanced_tools.py`

### 成就探针增强 + 游戏侧错误定性

**成就探针**新增 `mgr.config[1]` / `mgr.config[最后]` 完整内容导出（找 Steam 名/定义的字段结构）。实机结果：`config` 共 98 条（achId → 定义表），`已解锁=81，未解锁=0`。

**游戏侧 `entry/undefined` 定性**：定位到 `coui` 日志
```
[ERROR] JS Error: coui://build/components/Building.js:1127: TypeError: Cannot read properties of undefined (reading 'length')
[WARNING] ResourceRequestJob | Failed loading resource: coui://build/assets/entry/entry/undefined
```
回溯历史：`Building.js:1127` 在 **09-11 起每个会话都出现**（09-11×5、09-12×5、09-13/14×3）→ **游戏自身 UI bug，非本项目引起**。

**涉及文件**：`src/advanced_tools.py`

### 成就解锁修复（挑战成就 ID > 99）

**根因（游戏源码 `LAchievementMgr.lua:466`）**
```lua
function LAchievementMgr:GM_UnlockAllAchievement()
    for achId = 1, 99 do  -- ← 只覆盖 1..99
        if not self.unlockState[achId] then
            local bRet, g,d,p,l = g_LAchieveCardManager:GetGDPLById(achId);
            if bRet then g_LAchieveCardManager:UnlockAchieveCard(g,d,p,l); end
            self.unlockState[achId] = true;
        end
    end
end
```
→ 挑战成就（月落峡超甲通关 / 月落峡三金牌通关）的 ID **大于 99**，永远不在范围内 → 这就是“就差这俩”的原因。

**修复**
- `LUA_STEAM_ACHIEVEMENT_UNLOCK_ALL`：循环由 1..99 放大到 **1..300**，逐 id 走 `GetGDPLById` + `UnlockAchieveCard` + `unlockState[id]=true`；返回新解锁/已有/无此ID/失败明细；超时 8s→40s
- `LUA_STEAM_ACHIEVEMENT_PROBE` 新增「成就清单（1..300）」：`已解锁 / 未解锁` 计数 + **未解锁 ID 列表**（带 GDPL）

**验证**：py_compile OK；verify.py 通过；3 项自检全 True

**涉及文件**：`src/advanced_tools.py`

### GBK 结果解码修复 + 建筑字段修正

**新 bug（日志 23:35:34 证据）**
```
[ERROR] 读取结果失败: 'utf-8' codec can't decode byte 0xc7 in position 771
```
游戏内字符串含 **GBK 字节**（NPC 名、城市名等），`lua_result.txt` 以 utf-8 读失败 → **整条探查结果被丢弃**。
修复：改为二进制读 + utf-8 失败回退 `gbk(errors="replace")`。

**建筑明细字段修正**：`GetLevel`/`GetGDPL` 实机不存在 → 改用真实字段 `nAddRangeLevel` / `m_szGDPKey` / `m_nStatus`。

**实机验证（新机制均正常）**
- 速度：`基准 2.5 -> 4x=0.625 / 3x=0.833`；重复点击**不叠加**；速度状态显示 `游戏原始值=2.5`、`推导倍率=4`
- 灾害探查：能列出全部 21 个 DisasterType + `激活灾害数`（当时为 0）
- 建筑 `class 方法` 揭示游戏自带 GM 接口：`GM_UnlockAllAchievement` / `TalentUnlockAll` / `AdviserMaxLevel` / `CityBoomUp` 等（均在**建筑对象**的 class 上）

**涉及文件**：`src/lua_engine.py`、`src/world_tools.py`

### 季节合理化 + 灾害关闭真正生效

**问题 1：7月的冬天（不合理）**
- 旧实现只 hook `GetCurSeason` 返回固定季节，**不动日期** → 日历还是 7 月却显示冬天
- 修复：设置季节时**同步日期**，把月份落入该季节区间（春=1~3 / 夏=4~6 / 秋=7~9 / 冬=10~12），并回写 `m_nDayStamp=(月-1)*30+日`；输出带**当前日期**便于核对

**问题 2：零天灾/零人祸 关不掉（实机 0 命中）**
- 根因：旧实现把 `DisasterType` 的数值当键去调 `block:GetActiveDisaster(type)`，而 `LDisasterMgr.m_tbDisasters` 的键与判活路径不一致 → 扫描 1197 个「类型×地块」组合全 0 命中
- 修复：改为**直读 `block.m_disasterMgr.m_tbDisasters`**（游戏真实存储，键=灾害ID），用 `dis:IsActive()` 判活 + `dis:SetActive(false)` 关闭（游戏自身也用它结束灾害，见 `LFloodDisaster.lua:502`）
- 新增反向映射 `数值ID -> 名称`，按名称分类：**人祸 = DT_CRIME / DT_RIOT / DT_REFUGEE**，其余为天灾
- 探查输出新增：激活灾害列表（分类 + 名称 + ID）

**验证**：py_compile OK；verify.py 通过；UI 冒烟 SMOKE OK；4 项自检全 True

**涉及文件**：`src/world_tools.py`、`src/advanced_tools.py`

### 【真凶】时间跳过失控：m_nDayStamp 语义误用

**实机日志证据**：`跳过 1 天 -> 35年4月9日`、`跳过 7 天 -> 40年4月23日`、`跳过 1 个月 -> 45年6月3日`、`跳过 3 个月 -> 50年9月16日` —— **每跳一次滞约 5 年**。

**源码定性（`LTimeManager.lua:997`）**
```lua
self.m_tb.m_nDayStamp = nDayStamp or (month-1)*TimeDefine.DAY_PER_MONTH+day;
```
→ `m_nDayStamp` 是**年内第几天(1~360)**，不是累计天数。旧实现 `totalDays = dayStamp + days` 且回写 `nDayStamp=totalDays` → **逐年滚雪球**，连带让游戏逻辑失衡（表现为“速度/时间不受控”）。

**修复**
- 跳天/跳月改为**只用 年/月/日 推算**（360 天历法），不使用 dayStamp
- 回写 `m_nDayStamp = (newMonth-1)*30 + newDay`（符合游戏语义）
- 单次上限 3600 天（10 年），防失控
- 输出改为 **前→后** 双日期，便于核对

**同时修复**
- `__trainer_dump` 增补：展开 Lua 类对象的 `obj.class` 方法表（建筑等方法是 Lua table，之前看不到）
- NPC 探针增补：`GetCityInfoList()` / `m_lsCityInfo` 抽样导出

**日志其他结论（无需改）**：时间速度按钮绑定正确（0/1/2/3/4）；谋士升满级**已成功**（8 名）；建筑 295 个升级/满人口成功；23:09 的 `请求ID不匹配/超时` 为游戏繁忙+状态刷新并发所致（已有请求ID防护）

**涉及文件**：`src/advanced_tools.py`、`src/lua_lib.py`、`src/world_tools.py`

### 时间速度：语义定性与二次修复

**源码定性（`timer.lua` / `game_world.lua`）**
```lua
local TICK_DELTA_TIMES = _G.define.DAY_TIME_REAL / _G.define.DAY_TICK_COUNT  -- = 5/2 = 2.5
if fLastDeltaTime >= TICK_DELTA_TIMES + nNum then
    self:_Tick(TICK_DELTA_TIMES, self.tbRegister)
    fLastDeltaTime = fLastDeltaTime - TICK_DELTA_TIMES
```
→ TICK_DELTA_TIMES 是「每 tick 推进的仿真步长」同时又是 tick 触发阈值：
**仿真时间速率不随它变**（(1/delta)*delta = 1），它变的是**粒度**；而“按 tick 计数”的系统会被成倍放大 → 这才是“速度不受控”的本质，也是为何 2x/3x/4x 表现不稳定。

**修复**
- 基准/还原一律使用游戏权威原始值 `define.DAY_TIME_REAL / define.DAY_TICK_COUNT`（不再是内存快照），跨会话也不会错
- `LUA_TIME_SET_SPEED` 保留 last_delta 防叠加
- 「🔍 速度状态」额外显示游戏原始值
- 满天赋加兵库：`g_TalentManager` 为空时全局搜 `*Talent*`（该类在卸载场景时会被置 nil）

**验证**：py_compile OK；verify.py 通过；6 项自检全 OK

**涉及文件**：`src/advanced_tools.py`

### 时间速度修复（速度不受控）

**根因（两个，均会导致失控）**
1. `LUA_RESTORE_TIME_SPEED` 兜底硬写 `0.016`（实机基准为 **2.5**）→ 一旦触发等于 ~156 倍速
2. 基准 `g_trainer_orig_tick_delta` 只在**首次**记录；游戏自身改动 TICK_DELTA_TIMES 后再应用 → 基准错位、速度叠加

**修复**
- 重写 `LUA_TIME_SET_SPEED`：基准 `g_trainer_base_delta` + 上次写入 `g_trainer_last_delta`；检测到游戏改过速度（当前值≠上次写入值）则**自动重取基准**，杜绝叠加
- `LUA_RESTORE_TIME_SPEED` 改为还原基准值；无基准时**不改动**并提示（不再写 0.016）
- 新增 `LUA_TIME_SPEED_STATUS` + `get_time_speed_status()` + 高级页「🔍 速度状态」按钮（显示基准/当前/推导倍率），并纳入全量探查
- 时间诊断脚本同步改显示 base/last

**验证**：py_compile OK；verify.py 通过；0.016 残留=False；get_time_speed_status 存在

**待实机确认**：TICK_DELTA_TIMES 的倍率方向（变大=变快 or 变慢）

**涉及文件**：`src/advanced_tools.py`、`src/gui/tab_advanced.py`、`src/gui/tab_settings.py`

### 日志排查修复（实机日志 + 探查报告驱动）

**P0 修复（均由实机日志定位）**
- `config.py` 热键默认值仍是硬编码 11 个（`hotkey_defs` 只被热键页引用）→ 精华热键进不了配置。实机日志「已注册 12 个」但「已启用 11 个」印证。改为 `get_default_hotkeys()`
- `lua_lib.LUA_TRAINER_LIB` 末尾无返回值 → 注入校验恒为「未确认: 0」；补 `return 1`
- **pcall 型脚本成功不返回**继续补全：`resource_editor.py` 的 `LUA_ZERO_RESOURCES` / `LUA_RESTORE_HAPPINESS`（`if not ok then return 0 end` 后缺 `return err`）；全项目扫描已 0 残留

**功能修复（按实机探查结果）**
- `LUA_ADD_FAME` 重写：原实现靠猜字段名（m_nFame/m_nReputation…）→ 必然失败；改为 `g_LReputationMgr:ChangeReputation` + `ChangeReputationBase` 双存储
- 灾害分类改为实机确认枚举：**人祸 = DT_CRIME / DT_RIOT / DT_REFUGEE**，其余为天灾
- NPC 探针改用真 API：`g_CityManager:GetActiveCity()`（原 `m_lActiveCity` 实机确认为 **nil**）
- 建筑明细新增抽样建筑导出（找等级/GDPL getter）
- 新增 `__trainer_dump`（读 metatable 绑定方法），市场/产业链/地块/谋士/成就探针均接入

**实机确认**
- 矿产/木料映射**正确**（点哪个涨哪个）→ 知识库部分文档记反，以实机为准
- 知名度双存储生效（0 → 210000）
- 灾害类型枚举已完整拿到（DT_FIRE=1 … DT_REFUGEE=16 … DT_SANDSTORM=19）

**验证**：py_compile OK；verify.py 通过；load_config 热键 12 个含 essence

**涉及文件**：`src/config.py`、`src/lua_lib.py`、`src/lua_engine.py`、`src/resource_editor.py`、`src/world_tools.py`、`src/advanced_tools.py`、`src/resource_defs.py`、`src/gui/tab_settings.py`

### 探查报告：一键全量探查 + 结果落盘

**背景**：逐个点「探查」再把输出逐个复制给开发者很麻烦。

**改动**：
- `src/logger.py` 新增 `get_report_path` / `append_report` / `clear_report` / `read_report`，结果统一落到 `%LOCALAPPDATA%\woldvein_trainer\logs\probe_report.txt`
- 应用设置页新增「探查报告」卡片：**🧪 一键全量探查**（跑完 19 项探查/诊断，写入同一报告）/ **📄 打开报告文件** / **🗑 清空报告**
- 单点探查也自动落盘：世界系统（`_world_probe_worker`）+ 高级工具（品阶/地块/谋士/成就）

**验证**：py_compile OK；报告读写冒烟通过（写入/包含/清空/落盘均 True）

**涉及文件**：`src/logger.py`、`src/gui/tab_settings.py`、`tab_world.py`、`tab_advanced.py`

### 精华资源 + 灾害控制 + pcall 返回修复（实机测试反馈）

**P0 修复：pcall 型 Lua 脚本成功时不返回结果**
- 现象：点击「探查」无任何输出
- 根因：`local ok, err = pcall(f)` 成功时 `err` 装的是函数返回值，但脚本结尾没有 `return`，DLL 拿到空结果 → 界面无产出
- 修复：在收尾行后补 `return err`（`world_tools.py` 14 处 + `advanced_tools.py` 11 处，共 25 处）
- 影响面：**所有** pcall 型脚本（含原有品阶/地块/谋士/成就）之前都是“静默无结果”，本次一并修好

**新增：精华资源（ID 25）**
- `resource_defs.py` 加 `{id:25, name:"精华", key:"essence", icon:"✨", hotkey_key:"essence"}`
- 热键 `Ctrl+F11` 精华 +100万（`hotkey_defs.py`，12 个热键）
- `LUA_GET_STATUS` 补 `status.essence = m_tbSource[25]`
- **统一资源定义源**：`resource_editor.py` 不再自维护 `RESOURCES`，改为 `from .resource_defs import RESOURCES`（之前两份列表并存，精华只会一半生效）
- `tab_resource.py` 的硬编码 `id_to_field` 改为 `get_id_to_field()`

**新增：灾害控制面板（世界系统页）**
- **零天灾** / **零人祸** + 灾害探查；按 `game_world_define.DisasterType` 字段名关键词分类（水災/地震/饥荒… vs 流民/叛乱/犯罪…）
- 关闭方式：`block:GetActiveDisaster(type)` → `dis:SetActive(false)`（+ Close/EndDisaster 兵库）

**验证**：py_compile OK；`verify.py` 通过；资源 10 项 / 热键 12 个 / 灾害函数 3 个自检通过

**涉及文件**：`src/world_tools.py`、`src/advanced_tools.py`、`resource_defs.py`、`resource_editor.py`、`hotkey_defs.py`、`lua_engine.py`、`src/gui/tab_world.py`、`tab_resource.py`、`AGENTS.md`、`README.md`、`WORK_CONVENTIONS.md`、`docs/用户手册.md`

### 浅色主题完善：硬编码色收敛 + 切换重绘

**背景**：`tab_resource`/`tab_creative`/`tab_monitor`/`tab_settings`/`tab_advanced`/`tab_hotkey`/`diagnostic_panel`/`toast`/`tooltip`/`main_gui` 中大量 `tk.Frame/Label/Entry/Text` 硬编码深色十六进制色（`#313244`/`#1e1e2e`/`#cdd6f4` 等），浅色主题下颜色错乱。

**改动**：
- **127 处**硬编码色值 → `T("bg_card")` / `T("fg")` / `T("accent")` / `T("success")` 等主题取色
- `src/gui/widgets.py` 新增 `build_recolor_map` / `recolor_widget_tree`：tk 原生控件不随 ttk 样式自动变色，主题切换时按 `{旧色值: 新色值}` 递归重绘整棵控件树
- `main_gui.toggle_theme` 接入重绘；修正 `ThemeManager.get_theme()` 误用（应为模块级 `get_theme()`）——由冒烟测试捕获

**验证**：主题切换冒烟测试通过（resource 页某行背景 `#313244` → `#ffffff`，MATCH）

**涉及文件**：`src/gui/widgets.py`、`main_gui.py`、`tab_resource.py`、`tab_creative.py`、`tab_monitor.py`、`tab_settings.py`、`tab_advanced.py`、`tab_hotkey.py`、`diagnostic_panel.py`、`toast.py`、`tooltip.py`

### UI 重构：顶部 Notebook → 左侧导航（PCL2 风格）

**布局改造**（`src/gui/main_gui.py`）：
- 删除 `ttk.Notebook`，改为 **左侧导航（140px）+ 右侧内容区 + 底部可折叠日志**
- 6 个页面全部改为 `tk.Frame` 堆叠，用 `pack` / `pack_forget` 切换；新增 `_make_page` / `_show_page`
- 底部日志默认**收起**，点击标题栏展开/收起（`_toggle_log_panel`）
- 窗口尺寸：配置为空时按屏幕 80% 计算（上限 1280x800），`minsize` 700x500 → **900x620**

**页面套滚动**：`tab_resource` / `tab_creative` / `tab_monitor` / `tab_settings` 新增 `ScrollableFrame`；`tab_advanced` / `tab_world` 已用滚动，改为接收 `parent`
**主题**（`src/gui/theme.py`）：新增 `Nav.TButton` / `NavActive.TButton` 样式；`tab_advanced` 折叠面板硬编码色 `#313244`/`#45475a` → `T("bg_card")`/`T("bg_elevated")`；`tab_world` 行背景/提示色 → `T(...)`
**清理**：删除 `tab_hotkey.py` 中未被调用的死方法 `_build_hotkey_tab`（59 行）

**验证**：`py_compile` 通过；UI 冒烟测试（构建窗口 + 切页 + 日志折叠）通过；6 个页面均含 `ScrollableFrame`

**涉及文件**：`src/gui/main_gui.py`、`theme.py`、`tab_resource.py`、`tab_creative.py`、`tab_monitor.py`、`tab_advanced.py`、`tab_world.py`、`tab_settings.py`、`tab_hotkey.py`、`main.py`、`AGENTS.md`、`README.md`、`HANDOVER.md`、`WORK_CONVENTIONS.md`、`docs/用户手册.md`、`docs/PRD_v0.1.md`

### 新功能：世界系统标签页（方向6）

**新增标签页「世界系统」**（`src/gui/tab_world.py` + `src/world_tools.py`），标签页总数 5 → 6：
- **市场物价**：探查 `g_LMarketManager.m_prices[trandID][solarTerm+1]`，价格 ×0.5 / ×2，一键还原（操作前自动快照）
- **产业链**：`g_BuildingIndustryChain:SetUnlockState(true)` 全产业链解锁
- **流民灾害**：`block:GetActiveDisaster(DT_REFUGEE)` → `CleanAllUnacceptedRefugees` / `SuppressUnacceptedRefugeesRiot`
- **知名度**：修正为双存储同时修改（`ChangeReputation` + `ChangeReputationBase`）
- **建筑精细**：建筑明细（UUID/等级/GDPL）、`UpgradeToTop` 升级到顶、`GM_FullAllPopulation` 全部满人口
- **蓝图 / NPC 详情**：仅探查（API 未在游戏源码中确认，先探查再定制）

**设计**：所有脚本采用「探查 + 防御式执行」，动作逐项 pcall 并回报成功/失败计数；参数化脚本用 `__PLACEHOLDER__` + `str.replace` 注入，避免 Python `%` 与 Lua `%d/%s` 冲突。

**涉及文件**：`src/world_tools.py`（新）、`src/gui/tab_world.py`（新）、`src/gui/main_gui.py`、`main.py`、`AGENTS.md`、`README.md`、`HANDOVER.md`、`WORK_CONVENTIONS.md`、`docs/用户手册.md`、`docs/PRD_v0.1.md`

### 文档同步 + 模块化重构

**文档同步：** README / AGENTS / 用户手册 / PRD / HANDOVER / WORK_CONVENTIONS 口径统一 —— 标签页 5 大（资源修改 / 创造模式 / 游戏监控 / 高级工具 / 应用设置）、热键设置标注为独立工具 `hotkey_configurator.py`、资源数 9 种、打包口径 onedir 目录模式、配置项补 `theme`；新增文件（`hotkey_defs.py` / `resource_defs.py` / `lua_lib.py` / `async_helper.py` / `widgets.py` / `theme.py` / `scrollable.py` / `toast.py` / `tooltip.py`）补入目录结构。

**独立修复：** 托盘切换热键崩溃（`_tray_toggle_hotkey` 依赖未创建控件）、默认热键 F10/F12 写反、资源页 Tooltip 热键错位、恢复季节变量名不匹配（`g_trainer_orig_*` → 操作 `g_Time`）、建筑解锁诊断换行（`\\n` → `\n`）、`g_LHBUI:Emit` 与 `g_LHBUIProvider:EmitTo` 混用、`theme.py` 补 `Warning.TButton` / `Card.TCheckbutton`、打包后找不到热键配置工具（`_MEIPASS` 路径）。

**模块化：** 新增 `hotkey_defs.py` / `resource_defs.py` / `lua_lib.py` / `async_helper.py` / `widgets.py`，收敛热键定义（`get_default_hotkeys` / `get_hotkey_names` / `get_resource_hotkey`）、资源定义（`RESOURCES` / `get_id_to_field`）、Lua UI 事件（`__trainer_emit`）、hook 保存/还原（`__trainer_hook` / `__trainer_unhook`）、异步执行与按钮冷却（`run_async` / `CooldownButton`）、颜色取用（`T()` / 控件工厂）五类重复定义。

### 修改器 v0.3 发布（功能扩展 + UI 优化 + 性能提升）

**新功能（高级工具页）：**
- 城市品阶逐级提升：`g_camp.boom:setBoom(level+1)` 逐级 +1（基于知识库确认的 LCampBoom API）
- 全地块解锁：`g_blockMgr:GetAllBlocks()` + `BuyBlock()/PurchaseBlock()`（hook 购买条件检查放行）
- 谋士升满级：`g_LOfficeManager` 获取谋士 + `AddExp()/Upgrade()/SetSalary(0)/SetSalaryToSatisfy()/AddTrainAbility()`（忠诚度/能力满、薪资0）
- Steam 全成就解锁：`g_LAchievementMgr:GM_UnlockAllAchievement()`（mod_loader.lua 已确认的 GM 方法）
- 反向恢复按钮组：时间速度/季节/游戏暂停/资源归零/幸福度恢复

**UI 优化：**
- 深/浅主题切换（Catppuccin Mocha + Latte 色板），新增 `src/gui/theme.py`
- 侧边滚动条（内容超出自动滚动），新增 `src/gui/scrollable.py`

**性能优化：**
- `psutil` 懒加载（`find_game_process` 内导入，加速启动）
- 打包从 onefile 改为 onedir（消除单文件解压 2-5 秒延迟）

**Bug 修复：**
- `tab_hotkey.py` 误删 `log_success`/`log_warning` 导入导致 `NameError`（`_enable_hotkeys_silent` 运行时崩溃）
- 启动日志精简（去掉 3 条重复日志）
- trainer.c 版本号同步 v0.3 + DLL 重新编译

**涉及文件：** `src/advanced_tools.py`、`src/gui/tab_advanced.py`、`src/gui/tab_resource.py`、`src/gui/theme.py`（新）、`src/gui/scrollable.py`（新）、`src/gui/tab_hotkey.py`、`src/injector/__init__.py`、`src/injector/trainer.c`、`src/game_status.py`

## 2026-09-12

### 项目交接准备：日志更新 + 交接文档 + 缓存清理

- 更新所有项目日志（CHANGELOG.md、根目录AGENTS.md、修改器AGENTS.md）
- 撰写项目交接文档 `HANDOVER.md`
- 清理所有 `__pycache__` 缓存目录

### 修改器 v0.2 时间控制修复（第九轮，知识库查证）

**问题：高级工具中时间加速和季节变换失效**

**根因定位（查阅知识库 `75_时间管理器_LTimeManager.md`）：**
1. 全局对象名是 `g_Time`，不是 `g_TimeManager`（代码中7处用错）
2. 直接修改 `tm.m_tb.m_nTimeSpeed` 内部字段不生效——游戏在其他地方缓存了速度值
3. UI事件触发方式错误：用了 `g_LHBUI:Emit()`，正确方式是 `g_LHBUIProvider:EmitTo("LSystemProvider", event, data)`

**修复：**
- 时间加速：优先调用官方 `g_Time:SetTimeSpeed(speed)` 方法（会正确更新内部状态和缓存），直接改字段作为兜底
- 季节变换：优先调用官方 `g_Time:SetSeason(season)` 方法（会触发 `_whenTimeGoOn` 回调）
- UI事件：统一改用 `g_LHBUIProvider:EmitTo("LSystemProvider", ...)`
- NPC管理器路径修正：`g_CityManager.m_lActiveCity.m_lCityNpcMgr`（不是 `g_LCityNpcManager`）
- 文件：`src/advanced_tools.py`

### 修改器 v0.2 GUI代码重构：main_gui.py 拆分为 Mixin 模式

**背景：** `main_gui.py` 约1800行，单文件过大难以维护。

**拆分方案（Mixin模式，不改业务逻辑，只搬家）：**
- `main_gui.py`（436行）：主类、`__init__`、窗口/样式设置、顶部栏、日志面板、托盘、进程检测、注入、main函数
- `tab_resource.py`（108行）：资源修改标签页
- `tab_creative.py`（98行）：创造模式标签页
- `tab_save.py`（359行）：存档编辑+存档管理标签页
- `tab_hotkey.py`（187行）：热键设置标签页
- `tab_monitor.py`（223行）：游戏监控标签页
- `tab_advanced.py`（167行）：高级工具标签页
- `tab_settings.py`（242行）：应用设置标签页

**关键修复：**
- 新增 `src/__init__.py` 和 `src/gui/__init__.py`（相对导入必需）
- 修复 `tab_settings.py` 导入不存在的 `clear_log_file` 函数（在 `logger.py` 中补实现）
- 清理各文件冗余import
- `TrainerApp` 继承所有6个Mixin（存档编辑已移除，见下）

### 存档编辑器独立成工具

**需求：** 用户要求"存档编辑单独做一个工具，然后从修改器踢出去"。

**实施：**
- 创建独立项目 `D:\pingye_pack\save_editor_tool\`
- 功能：存档管理（扫描/重命名/index同步/备份清理）+ 存档内容编辑（解密/JSON编辑/保存）
- 深色主题GUI，游戏路径可配置
- 打包 `save_editor_v1.0.exe`（13.4MB）
- 从修改器移除 `SaveTabMixin`，标签页从7个减为6个
- 修复移除后残留的 `app.on_refresh_saves()` 调用错误（导致启动崩溃）
- 修改器重新打包（32.1MB）

### 散文件MOD管理功能

**背景：** 游戏目录存在 `sim_common/` 散文件版创造模式，可能与DLL注入版冲突。

**新增功能（应用设置页）：**
- 检测散文件MOD安装状态
- 安装散文件MOD按钮（从 `creative_mode_v1.0/sim_common` 复制到游戏目录）
- 卸载散文件MOD按钮（删除游戏目录的 `sim_common/`）
- 文件：`src/gui/tab_settings.py`

### 创造模式建筑解锁方案探索与回退

**问题：** 用户反馈"创造模式下建筑还是未解锁，只有最初的那几个"，后续"之前还是被解锁有解锁的，现在连解锁都没有了"。

**探索过程：**
1. 初始方案：hook `GetUnlockState`/`SetUnlockState` + `scheme:SetBuildingCardState` → 部分有效
2. 三层突破方案：hook `g_LBuildingProvider.RefreashBuildingCardUnlockState` + 直接设 `_bUnlock=true` + hook `CheckTalentIsActive` + 调用 `UpMaxAllTalent()` → 反而破坏了建筑解锁
3. 回退：移除有副作用的 `UpMaxAllTalent()` 调用和 `g_LBuildingProvider` hook，只保留卡片hook+天赋检查hook

**已验证死路：**
- `g_LBuildingProvider` 不是全局变量（是UI Provider，通过 `g_LHBUIProvider:EmitTo` 通信）
- `UpMaxAllTalent()` 调用可能触发游戏内部状态重置反而锁定建筑
- 用 `SetUnlockState(false)` "隐藏"低等级建筑 → 实际是锁定，与全解锁冲突

**待解决：** 建筑解锁的正确实现方式仍需进一步调试，可能需要在游戏运行时用Lua命令探测实际的建筑解锁状态。

### BAT启动脚本

- 创建 `启动修改器.bat`（纯英文，避免中文编码问题）
- 功能：检查Python环境 → 安装依赖（psutil/keyboard/pystray/pillow）→ 启动修改器
- 修复中文BAT在cmd下乱码问题

### 修改器 v0.2 Bug修复（用户反馈2项）

**1. 建筑升级bug：单等级建筑（如谋士府）点击升级会播放升级动画**
- 原因：创造模式中 `CheckCanUpgradeBuilding` 被hook为 `function() return true end`，所有建筑都允许升级
- 修复：hook函数先调用原始函数，原始返回false时检查建筑最大等级：最大等级>1且当前等级<最大等级→允许升级；最大等级=1或已满级→不允许升级
- 文件：`src/lua_engine.py`

**2. 清空日志按钮无效：只清空GUI显示，未清空日志文件，且无成功提示**
- 原因：`on_clear_log` 只调用 `self.log_text.delete()`，未操作日志文件
- 修复：`src/logger.py` 新增 `clear_log_file()` 函数（关闭句柄→清空文件→重新打开）；`on_clear_log` 调用后弹出成功/失败提示
- 文件：`src/logger.py`、`src/gui/tab_settings.py`

## 2026-09-11

### 修改器 v0.2 Bug修复（用户反馈2项）

**1. 建筑升级bug：单等级建筑（如谋士府）点击升级会播放升级动画**
- 原因：创造模式中`CheckCanUpgradeBuilding`被hook为`function() return true end`，所有建筑都允许升级
- 修复：hook函数先调用原始函数，原始返回false时检查建筑最大等级：
  - 最大等级>1且当前等级<最大等级 → 允许升级（解锁等级限制）
  - 最大等级=1或已满级 → 不允许升级（避免单等级建筑播放升级动画）
- 文件：`src/lua_engine.py`

**2. 清空日志按钮无效：只清空GUI显示，未清空日志文件，且无成功提示**
- 原因：`on_clear_log`只调用`self.log_text.delete()`，未操作日志文件
- 修复：
  - `src/logger.py`新增`clear_log_file()`函数（关闭句柄→清空文件→重新打开）
  - `on_clear_log`调用`clear_log_file()`，成功弹出"日志已清空"提示，失败弹出错误提示
- 文件：`src/logger.py`、`src/gui/main_gui.py`

### 修改器 v0.2 Bug修复（第八轮，用户反馈"大部分没改"后的全面核查+补修）

**核查结论：上一轮修复实际已生效，用户看到的可能是旧版本。本轮补修3处遗漏：**

1. 补修 `trainer.c` `execute_lua` 孤立注释"保存栈顶..."（上一轮匹配失败未删除）
2. 补修 `creative_mode.py` "完整还原"→"尝试还原"、"39项"→"遍历g_functionType"
3. 补修 `main_gui.py` "8大功能模块"→"7大"、"构建8个标签页"→"7个"

**已确认修复的项（上一轮已生效，本轮复核通过）：**
- P0键名：`__cm_orig_CheckCanCreate`/`__cm_orig_CheckCanUpgrade` 已对齐，无带Building后缀的错误键名
- 死代码：`__cm_hide_hooked`/`__cm_adv_saved` 已删除
- opcode：`0x81` = `0x07`（imm32+ModR/M）
- trainer.c头部：IAT/rawset/lua_settable/"每帧"残留已清除
- 路径：logger/config/save_editor 三文件均已用LOCALAPPDATA优先
- save_manager：复用save_editor.BACKUP_DIR
- game_monitor：8处裸except已改为except Exception
- config：fame注释+10000

**12项验证全部PASS（第1项为验证脚本正则过宽误报，精确复核已确认修复）**

### 修改器 v0.2 Bug修复（第七轮审查，P0键名不一致+自检）

**P0严重错误（1项）：**
1. 修复 `LUA_CREATIVE_DISABLE` 第2步键名不一致（最严重）：
   - ENABLE保存的是 `__cm_orig_CheckCanCreate` / `__cm_orig_CheckCanUpgrade`
   - DISABLE读的是 `__cm_orig_CheckCanCreateBuilding` / `__cm_orig_CheckCanUpgradeBuilding`
   - 键名不匹配导致永远走else分支，`CheckCanCreateBuilding`/`CheckCanUpgradeBuilding`被置nil
   - 关闭创造模式后建造/升级功能会坏掉，已对齐键名

**P1中等问题（3项）：**
2. 修复 `trainer.c` opcode表 `0x81` 从 `0x03` 改为 `0x07`（上一轮给错了，0x81有ModR/M+imm32，属性应为imm_code=3+has_modrm=1=0x07）
3. 修复 `save_manager.py` `clean_backups` 打包后路径错位（复用 `save_editor.BACKUP_DIR`）
4. 修复 `logger.py`/`config.py`/`save_editor.py` 打包后写EXE目录可能失败（统一改为 `%LOCALAPPDATA%\woldvein_trainer\` 优先）

**P2轻微问题（1项）：**
5. 修复 `game_monitor.py` 8处裸 `except:` 改为 `except Exception:`（避免吞掉KeyboardInterrupt/SystemExit）

**注释/文档修复（6项）：**
6. 修复 `config.py` fame注释 `+1000` → `+10000`
7. 修复 `AGENTS.md` "低等级建筑临时隐藏" → "只显示最高等级建筑"
8. 修复 `AGENTS.md` 标签页列表（存档管理合并到存档编辑，添加应用设置，统一7个）
9. 修复 `README.md` `PRD_v0.2.md` → `PRD_v0.1.md`（实际文件名）
10. 修复 `save_manager.py` 注释"打包后指向EXE同目录" → "优先LOCALAPPDATA"

**自检流程：**
- 全部Python文件语法检查通过
- DLL编译成功（57.1KB）
- 关键修复点逐项验证：键名无残留、opcode=0x07、三文件LOCALAPPDATA、无裸except

### 修改器 v0.2 Bug修复（第六轮审查25项，代码错误+注释错误一起修）

**真实错误（7项）：**
1. 修复 `LUA_CREATIVE_DISABLE` 误删游戏方法 `GetAdvancedUpgrade`（ENABLE从未保存`__cm_orig_GetAdvancedUpgrade`，DISABLE永远走else置nil）
2. 修复 `LUA_CREATIVE_DISABLE` 第0步死代码（`__cm_hide_hooked`从未被赋值）
3. 修复 `LUA_CREATIVE_DISABLE` 第5步死代码（`__cm_adv_saved`从未被赋值）
4. 修复 `save_manager.py` `clean_backups` 打包后路径错位（`__file__`在_MEIPASS下，复用`save_editor.BACKUP_DIR`）
5. 修复 `trainer.c` `execute_lua` 孤立注释（变量已删，注释描述的功能不存在）
6. 修复 `trainer.c` `opcode_table` `0xC2`/`0xC8` 立即数长度偏短（ret imm16固定2字节，enter imm16+imm8共3字节）
7. 修复 `config.py` 打包后config.json可能写在无权限目录（优先`%LOCALAPPDATA%\woldvein_trainer\`）

**注释与代码不一致（12项）：**
8. 修复 `trainer.c` 头部"IAT/Inline Hook"→"Inline Hook"（v0.2已弃用IAT）
9. 修复 `trainer.c` 头部rawset/lua_settable残留注释（当前代码无此逻辑）
10. 修复 `trainer.c` `my_lua_pcall` 注释"每帧"→"50ms间隔"
11. 修复 `lua_engine.py` 头部`_MEIPASS`注释→`%LOCALAPPDATA%`固定路径
12. 修复 `lua_engine.py` `LUA_GET_STATUS` 注释"幸福度和知名度"→"幸福度"（无知名度字段）
13. 修复 `creative_mode.py` "解锁全部39项功能"→"遍历g_functionType全部设为OPEN"
14. 修复 `creative_mode.py` "完整还原"→"尝试还原"（有死代码和误删，已修复后可恢复）
15. 修复 `main.py` "8大标签页"→"7大标签页"（存档管理合并到存档编辑）
16. 修复 `main_gui.py` "8大标签页"→"7大标签页"
17. 修复 `AGENTS.md` "低等级隐藏:SetUnlockState(false)"→"只显示最高等级建筑:hook GetBuildingCards过滤"
18. 修复 `trainer.c` 未使用变量 `has_67`、`imm_66_dependent`

**轻微问题（6项）：**
19. 修复 `main_gui.py` `on_toggle_creative` `ok`变量赋值未使用
20. 修复 `main_gui.py` `mon_mode` 初始文本和更新文本前缀不一致（统一为"模式:"）
21. 修复 `main_gui.py` `_do_refresh_resources` 静默吞异常（添加log_warning）
22. 修复 `README.md` 项目结构缺 `save_manager.py`/`game_monitor.py`/`advanced_tools.py`
23. 修复 `README.md` 依赖不全（添加 `pystray pillow`）
24. 修复 `README.md` DLL/EXE大小过时
25. 修复 `lua_engine.py` 注释中`\w`转义序列警告

### 修改器 v0.2 Bug修复（25项问题清单全部修复）

**严重错误（6项）：**
1. 修复 `trainer.c` 文件头多余的 `*/` 导致编译失败（删除中间注释结束符，保持连续注释块）
2. 修复 `trainer.c` opcode表 `0x81` 立即数长度错误（0x05→0x03，imm32=4字节）
3. 修复 `LUA_CREATIVE_ENABLE` 访问 `g_camp` 未判空（添加 `g_camp and` 检查）
4. 修复 `g_FunctionManager` 与 `g_functionManager` 大小写不一致（统一为大写F）
5. 修复 `LUA_CREATIVE_DISABLE` 第5步条件多余且错误（移除 `g_functionManager` 小写检查）
6. **修复通信路径最大隐患**：PyInstaller打包后 `sys._MEIPASS` 每次启动不同，导致重启修改器后功能全废。改为固定路径 `%LOCALAPPDATA%\woldvein_trainer\`，Python端和DLL端同步修改

**中等问题（7项）：**
7. 修复 `logger.py` `print(line)` 在 `--windowed` 打包下抛异常（添加 `sys.stdout is not None` 检查和try/except）
8. 修复 `save_manager.py` `dry_run` 预览计数始终为0（预览时也统计待处理数量）
9. 修复 `advanced_tools.py` `LUA_NPC_REMOVE_ALL` 在pairs遍历中删除元素（先收集临时表再销毁）
10. 修复 `main_gui.py` `mon_mode` 标签被创造模式和游戏模式互相覆盖（拆分为 `mon_mode`（游戏模式）和 `mon_creative`（创造模式状态）两个标签）
11. 修复 `injector/__init__.py` `is_dll_injected` 用 `psutil.memory_maps()` 在Windows上不可靠（改用 `EnumProcessModulesEx` + `GetModuleFileNameExW`）
12. 修复 `lua_engine.py` 超时后只删CMD_FILE未删RESULT_FILE（同时清理两个文件）
13. 修复诊断日志中「知名度」永远显示「未知」（LUA_GET_STATUS无此字段，移除该行）

**轻微问题/隐患（12项）：**
14. 修复 `advanced_tools.py` 多处硬依赖 `require("cjson")`（改用 `pcall(require, "cjson")`，失败时返回可读文本）
15. 修复 `advanced_tools.py` `LUA_NPC_ADD` 用 `%s` 拼Lua字符串（添加引号和反斜杠转义）
16. 修复 `hotkey_manager.py` `register` 与 `unregister` 大小写不一致（unregister也统一小写）
17. 修复 `config.py` `save_config` 对空目录路径抛异常（添加 `if parent:` 检查）
18. 修复 `trainer.c` `top_before` 未使用变量（删除）
19. 修复 `injector/__init__.py` `call_dll_export()` 半成品逻辑（删除该函数）
20. 修复 `main_gui.py` 多个Treeview无滚动条（给save_mgr_tree、hotkey_tree、mon_save_tree添加垂直滚动条）
21. 修复 `main_gui.py` `_re_register_hotkeys()` 冗余导入 `is_admin`（移除）
22. 修复 `game_monitor.py` `cpu_percent(interval=0.1)` 每轮阻塞100ms（改为 `interval=None` 非阻塞）
23. 修复 `save_manager.py` `clean_backups` 硬编码路径（自动定位项目backups目录）
24. 修复 `save_editor.py` `open_save` 中 `len(buf)` 对NULL buffer抛异常（添加 `if buf is None: buf=b""`）
25. 修复 `trainer.c` 通信路径与Python端不一致（同步改为 `%LOCALAPPDATA%\woldvein_trainer\`）

### 修改器 v0.2 发布
- 版本号从 v0.1 升级到 v0.2
- 全部源码添加详细注释（模块文档字符串、函数docstring、关键代码段注释）
- 覆盖14个源码文件：main.py, config.py, logger.py, lua_engine.py, resource_editor.py, creative_mode.py, save_editor.py, save_manager.py, hotkey_manager.py, game_monitor.py, advanced_tools.py, injector/__init__.py, injector/trainer.c, gui/main_gui.py

### 修改器 v0.2 Bug修复（代码审查第五轮）
- 修复 `hotkey_manager.is_admin()` 调用错误（实例无此方法，改为导入模块级is_admin函数）
- 修复热键切换创造模式后GUI状态显示错误（用is_creative_mode_enabled()而非操作返回值）
- 修复main()中root.protocol覆盖托盘关闭协议（删除重复设置，保留最小化到托盘）
- 修复LUA_CREATIVE_ENABLE中g_camp可能为nil导致创造模式开启失败（添加g_camp检查）
- 修复g_FunctionManager与g_functionManager大小写不一致（统一为大写F）
- 修复LUA_CREATIVE_DISABLE第5步条件错误（移除多余的g_functionManager小写检查）
- 修复save_manager.py dry_run预览计数始终为0（预览时也统计待处理数量）
- 修复logger.py print(line)在windowed打包下可能异常（添加try/except保护）
- 修复main_gui.py存档列表tooltip TclError风险（after_cancel取消旧定时器、局部变量捕获、try/except销毁）
- 修复advanced_tools.py LUA_NPC_REMOVE_ALL在pairs中删除元素（先收集到临时表再销毁）
- 修复lua_engine.py超时后只清理CMD_FILE未清理RESULT_FILE（同时清理两个文件）

### 空间清理
- 项目总大小从 1898 MB 降至 346 MB，释放约 1552 MB
- 删除：PyInstaller构建缓存、调试截图BMP、旧版本归档zip、development/archived/0.2~0.8、releases/v1.0.0/launcher、knowledge临时文件、所有__pycache__、空目录、重复src/src结构

### 修改器 v0.1 Bug修复（第四轮）
- 修复 `log_info` 未定义（21处，全部替换为 `log`）
- 修复 `find_game_process()` 返回元组格式错误（PID显示为整个psutil.Process对象）
- 修复资源ID映射搞反（id=2矿产/id=3木料在UI显示中颠倒）
- 新增DLL注入后Hook就绪验证：注入后异步执行 `return 1` 探测Lua通道连通性
- 新增修改器后打开时自动检测DLL已注入并静默验证Hook状态
- 修复 `not enough arguments for format string`（与log_info未定义的异常链相关）

### 修改器 v0.1 Bug修复（第三轮）
- 修复热键全部失效（pystray托盘初始化干扰keyboard全局钩子，调整初始化顺序）
- 修复建筑被锁（原用GetUnlockState=false隐藏低等级建筑实际是锁定，改用SetUnlockState+等级过滤）
- 修复等级满级但UI没改（setBoom(14)后添加S2UI_OnUpdateCampInfo事件刷新）

### 修改器 v0.1 Bug修复（第二轮）
- 修复升级全部冷却中点击立即完成失效（两个按钮共享冷却）
- 修复创造模式应用后建筑未解锁（重新实现全建筑解锁+只显示最高等级建筑）
- 新增应用设置页：诊断日志输出、日志路径显示、打开日志文件夹/文件、复制路径
- 新增游戏监控页复制错误信息按钮
- 新增启动游戏按钮进程检测（已运行则提示阻止重复启动）

### 修改器 v0.1 Bug修复（第一轮）
- 修复资源修改页木料和矿产搞反
- 优化创造模式开启卡顿（合并遍历、减少UI刷新、减少pcall嵌套）
- 修复热键全部失效（添加管理员权限检查、启用失败回滚）
- 修复游戏监控页游戏未开启时占用CPU（检测间隔改为5秒）
- 修复创造模式切换后监控页模式不同步
- 修复高级工具按钮无冷却导致游戏失控（添加3秒冷却）
- 修复暂停游戏/季节变换/时间加速/跳过天数失效（修正TimeManager API）

### 修改器 v0.1 功能扩展
- 新增游戏监控模块（第5标签页）：进程/内存/模式/存档/Lua错误/崩溃检测
- 新增高级工具模块（第6标签页）：NPC管理、时间天气、建造升级、SimWorld
- 新增存档管理模块（合并自eastfamily C#项目）：扫描/重命名/index同步/备份清理
- 新增应用设置页（第7标签页）：诊断工具、日志管理、关于
- 创造模式增强：全功能解锁（39项功能）、低等级建筑临时隐藏、关闭完整还原
- UI优化：Treeview深色主题、资源当前值实时显示、热键双击编辑、系统托盘

### 项目记忆更新
- 创建8个AGENTS.md：根目录总览、woldvein_trainer、v1.1 Agent、eastfamily、Tear-it-all-down、releases/v1.0.0、两个源码副本

### 散文件版创造模式
- 创建 `创造模式_v1.0.zip`（152KB）：6个Lua散文件+安装/卸载bat+README

## 2026-09-10

### 逆向工程阶段1-7完成
- 阶段1：预处理脱壳（无壳64位PE）、pak资源索引、Steam-XGSDK启动校验
- 阶段2：IDA静态分析，定位tolua，找到Core::SimWorld 41个方法，提取1580条静态绑定
- 阶段3：动态观测，observer注入框架，IAT-Hook→Inline-Hook Lua5X64.dll，全自动闭环
- 阶段4-7：DLL Hook全量观测、知识库整理、pak格式文档、权威绑定清单
- 产出：719类/13110方法权威绑定、Lua-C++交互完全手册（647KB/13028行）、动态原始日志13110条

### 三大决定性Bug修复
1. 定制Lua5X64.dll无lua_tostring导出，实际导出lua_tolstring，指针为NULL导致rawset跳过
2. rawset栈序判断颠倒，实测栈规则 v=-1, k=-2
3. lua_settable头部相对call跳转，inline-hook复制指令长度不足触发0xC0000005崩溃

## 2026-09-09

### MOD系统项目计划书
- 完成《城市建造经营游戏MOD系统开发项目计划书》终版
- 确立方案B：纯Lua散文件入口无注入（主方案）、DLL Hook（兜底方案）
- Phase0四项预验证实验设计

### 创造模式工具（初版）
- CreativeMode.dll + 启动创造模式.exe
- 测试失败后转向统一修改器方向

## 更早

- 1760个Lua脚本完整解包反编译
- 14986条Lua-C++交互API索引
- .boh存档加解密破解（ROR3+每16字节反转）
- mod_loader.lua原型（散文件方案）
- v1.0 MOD加载器+启动器发布

## v0.3 UI优化版 (2026-09-12)

### 全局与顶部导航
- 状态栏整合：DLL状态与按钮合并为统一状态指示灯
- 统一色彩系统：主操作蓝/成功绿/危险红/次要灰
- 内容区max-width居中

### 资源修改
- 9个资源卡片改为紧凑表格布局
- 快捷操作固定顶部
- Toast修改反馈+Tooltip热键提示

### 创造模式
- 修复HTML解析Bug（称号<span>标签）
- 全选/全不选功能选项
- 诊断结果高亮（成功绿/失败红）

### 热键设置
- 列表紧凑排版
- 恢复默认/清空全部热键

### 游戏监控
- 日志自动滚动复选框
- 存档行高缩小

### 高级工具
- 谋士/建造/SimWorld改为折叠面板
- 输出框占位提示+清空按钮

### 应用设置
- 路径脱敏显示（Tooltip完整路径）
- MOD冲突红色高亮

### 交互体验
- 防呆置灰（DLL未注入时）
- 全局Toast反馈（4种级别）
- 悬浮Tooltip提示

### 新增文件
- src/gui/toast.py
- src/gui/tooltip.py
