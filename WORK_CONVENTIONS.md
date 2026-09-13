# 工作约定 v2 — woldvein_trainer 项目

> 生效日期：2026-09-12
> 适用范围：woldvein_trainer 项目的所有代码改动、文档更新
> 核心原则：**没有证据块的结论，视为未检查。**

---

## 0. 分批规则

一次最多处理 **5 个文件**。超出 5 个，主动说"请分批给我"，不要一口气全看。

如果任务涉及超过 5 个文件，按以下优先级分批：
1. 第一批：核心模块（注入 + Lua 引擎）
2. 第二批：GUI 层（main_gui + 所有 tab）
3. 第三批：文档（README / AGENTS / 用户手册 / PRD）
4. 第四轮：交叉核对（汇总矛盾点）

---

## 1. 改动前声明

每次动手之前，必须先声明：

```
【改动声明】
级别：file-level / project-level
涉及文件：
  - 路径1
  - 路径2
涉及文档：
  - 路径1
  - 路径2
```

- **file-level**：改单文件内部，不影响其他文件
- **project-level**：改一个功能涉及多文件，或修改公共接口/常量

---

## 2. 证据块规则

**每条结论必须带"证据块"**，格式：

```
【证据块】
命令: <实际执行的命令>
输出:
<贴原始输出，可截断但不可编造>
结论: <基于输出的明确结论>
```

没有证据块的结论，视为未检查。

可截断的情况：输出超过 50 行时，贴前 20 行 + 后 20 行，中间用 `...(省略N行)...` 标注。

**禁止**：凭记忆回答、凭印象回答、"应该没问题"、"已检查完毕" 等无证据表述。

---

## 3. 不确定就写"未核对"

不要写"无问题"，除非你有证据块证明确实没问题。

- **"无问题"** = 我查了，有证据，没问题
- **"未核对"** = 我没查，或者查了但拿不准

如果写"无问题"但实际没查，视为故意欺骗。

---

## 4. 连带影响清单

改动后必须做"连带影响清单"，逐项列出：

```
【连带影响清单】
1. 改动项：<改了什么>
   引用方：
   【证据块】
   命令: grep -rn "标识符" src/
   输出: ...
   结论: 被 X 文件引用，已同步 / 未被引用，安全删除

2. 改动项：<改了什么>
   文档宣传：
   【证据块】
   命令: grep -rn "关键词" *.md docs/
   输出: ...
   结论: 文档已更新 / 文档需同步修改
```

一个都不许漏。

---

## 5. 数量/版本号全局同步

涉及"数量"的信息（标签页数、资源数、热键数、版本号、模块数），改动后必须全局搜索并贴结果：

```
【证据块】
命令: grep -rn "标签页\|6 个页面" . --include="*.py" --include="*.md"
输出:
src/gui/main_gui.py:6:    左侧导航 + 右侧内容页（PCL2 风格）GUI 界面，集成 6 个页面：
AGENTS.md:66:## 功能模块（左侧导航 + 6 个页面）
README.md:65:修改器共 **6 个页面**（左侧导航切换，内容超出可滚动）
结论: 全部一致，均为"左侧导航 + 6 个页面"
```

必须检查的文件范围：
- 代码：`src/` 下所有 .py
- 文档：`AGENTS.md`、`README.md`、`docs/用户手册.md`、`docs/PRD_v*.md`

---

## 6. 系统调用与异常处理

- 每个 Win32 API 调用（`OpenProcess` / `WaitForSingleObject` / `CreateRemoteThread` / `VirtualAllocEx` / `WriteProcessMemory` 等）必须有失败分支处理，不允许只写成功路径。
- 每个 `except` 必须至少 log 一行。禁止 `except: pass` 和 `except Exception: pass`，除非注释明确说明为什么必须静默。

见到一个报一个，不允许跳过。

---

## 7. 自查清单

改动完成后，回头读一遍自己的输出，检查以下项目，自查结果贴在末尾：

```
【自查清单】
1. 有没有"我保证"、"应该没问题"、"大致上"、"应该"这类模糊词？  [有/无]
2. 有没有漏掉第 4 条的连带影响清单？  [有/无]
3. 每条结论都有证据块吗？  [是/否]
4. 有没有"未核对"的部分？  [有/无，如有列出]
5. 有没有新增死代码（定义但从未被调用）？  [有/无]
6. 有没有新增未使用 import？  [有/无]
7. 有没有新增 except: pass？  [有/无]
```

---

## 8. 错误纠正规则

用户如果指出"你之前漏了 X"，不要辩解，直接按以下步骤：
1. grep 确认
2. 给出证据块
3. 改正
4. 说明为什么之前漏掉了

---

## 附：项目引用树（状态锚点）

> 每次改动前对照此树，指出改动影响了哪些节点。
> 最后更新：2026-09-13（新增 hotkey_defs / resource_defs / lua_lib / async_helper / widgets 等模块）

```
woldvein_trainer/
├── main.py                          ← 入口（引用 lua_engine + logger + main_gui）
├── verify.py                        ← 验证脚本（引用 config + resource_editor）
├── src/
│   ├── config.py                    ← 被 main_gui + tab_creative + tab_hotkey 引用
│   ├── logger.py                    ← 被 14 个文件引用（核心依赖）
│   ├── lua_engine.py                ← 被 creative_mode + resource_editor + advanced_tools + main_gui + main 引用
│   ├── resource_editor.py           ← 被 tab_hotkey + tab_resource 引用
│   ├── creative_mode.py             ← 被 tab_creative + tab_resource + tab_settings 引用
│   ├── advanced_tools.py            ← 被 tab_advanced 引用
│   ├── world_tools.py               ← 被 tab_world 引用（市场/产业链/流民/知名度/建筑精细）
│   ├── hotkey_manager.py            ← 被 main_gui + tab_hotkey + tab_settings 引用
│   ├── game_monitor.py              ← 被 main_gui + tab_monitor 引用
│   ├── injector/__init__.py         ← 被 main_gui 引用
│   ├── gui/
│   │   ├── __init__.py              ← 包标识（相对导入必需，不被直接 import）
│   │   ├── main_gui.py              ← 被 main.py 引用（核心GUI类）
│   │   ├── tab_resource.py          ← 被 main_gui 继承（Mixin）
│   │   ├── tab_creative.py          ← 被 main_gui 继承（Mixin）
│   │   ├── tab_hotkey.py            ← 被 main_gui 继承（仅热键回调，无 UI 构建）
│   │   ├── tab_monitor.py           ← 被 main_gui 继承（Mixin）
│   │   ├── tab_advanced.py          ← 被 main_gui 继承（Mixin）
│   │   ├── tab_world.py             ← 被 main_gui 继承（Mixin）
│   │   ├── tab_settings.py          ← 被 main_gui 继承（Mixin）
│   │   └── diagnostic_panel.py      ← 被 tab_creative + tab_advanced 引用
│   └── _archive/                    ← 历史归档（不参与构建和引用）
│       └── save_editor_legacy/
│           ├── save_editor.py
│           ├── save_manager.py
│           └── tab_save.py
```

**当前页面数量：6 个**（左侧导航切换：资源 / 创造 / 监控 / 高级 / 世界 / 设置）
**当前资源数量：10 种**（金钱/矿产/木料/衣物/食物/水/人口/盐/酒/精华）
**当前热键数量：12 个**（F1~F11 + F12）
**当前版本号：v0.3**

---

## 附：审问模板（用户用）

每次 AI 改完代码，直接复制这段问它：

```
按照【工作约定 v2】回答以下问题，每条必须带证据块（命令+原始输出），
没有证据块的回答视为无效：

1. 这次改动涉及哪些文件？(ls 出清单)
2. 这些文件里有没有别的地方引用了被删/改的东西？
   (grep 命令 + 输出)
3. 涉及的数量/版本号（标签页数、资源数、版本号），
   代码里、AGENTS.md、README.md、用户手册.md 分别是多少？
   (grep 命令 + 输出)
4. 这次新增/改动的标识符，在代码里能搜到定义吗？
   (grep 命令 + 输出)
5. 有没有新增 import 是原来就有的？(grep 命令 + 输出)
6. 有没有新增 `except: pass`？(grep 命令 + 输出)
7. 有没有新增 Win32 API 调用没处理失败分支？
8. 有没有死代码（定义但从未被调用）？(grep 命令 + 输出)
9. 你自己回头读一遍这份回答，有没有第 3 条规则里的模糊词？
10. 有没有"未核对"的部分？明确列出。

答不出证据块的，重做。
```
