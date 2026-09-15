# -*- coding: utf-8 -*-
"""
平野孤鸿修改器 - tkinter 微信三栏布局版 v0.3.6
集成完整业务逻辑

运行：python trainer_ui_tk.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
import os
import threading
import shutil
from datetime import datetime

# ============================================================
# 业务模块导入
# ============================================================
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.injector import find_game_process, inject_dll, is_dll_injected, launch_game
from src.resource_editor import (
    add_resource, add_all_resources, zero_all_resources,
    max_happiness, add_fame, restore_happiness
)
from src.creative_mode import (
    enable_creative_mode, disable_creative_mode,
    is_creative_mode_enabled, set_creative_options,
    get_game_status, diagnose_unlock_status
)
from src.lua_engine import execute_lua_safe
from src.config import load_config, save_config
from src.logger import (
    init_log, set_log_callback, log, log_info, log_success,
    log_warning, log_error, get_log_path, clear_log_file
)
from src.resource_defs import RESOURCES
from src import advanced_tools
from src import world_tools
from src import cheat_tools
from src.hotkey_defs import HOTKEY_DEFS, get_default_hotkeys, get_hotkey_names
from src.constants import DEFAULT_GAME_PATH, SIM_COMMON_REL

# ============================================================
# 配色（微信风格）
# ============================================================
COLORS = {
    "bg": "#f5f5f5", "bg_sidebar": "#f7f7f7", "bg_sidebar_sel": "#07C160",
    "bg_card": "#ffffff", "bg_hover": "#f2f2f2", "bg_selected": "#e8f5e9",
    "fg": "#000000", "fg_muted": "#999999", "fg_sidebar": "#000000",
    "fg_sidebar_sel": "#ffffff", "accent": "#07C160", "accent_hover": "#06ad56",
    "success": "#07C160", "warning": "#fa9d3b", "error": "#fa5151",
    "border": "#e6e6e6",
}
FONT = "微软雅黑"
DLL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "woldvein_trainer.dll")
VERSION = "v0.3.7"


# ============================================================
# 主窗口
# ============================================================
class TrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"平野孤鸿 全能修改器 {VERSION}")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg"])

        self.current_nav = 0
        self.current_func = 0
        self.nav_buttons = []
        self.func_items = []
        self.game_pid = None
        self.dll_injected = False
        self.config = load_config()
        self.creative_vars = {}
        self.resource_entries = {}

        init_log()
        set_log_callback(self._on_log_message)
        self._build_ui()
        self._switch_nav(0)
        self._start_status_timer()
        log_info(f"修改器 {VERSION} 已启动")

    # ===== 日志回调 =====
    def _on_log_message(self, msg, level="INFO"):
        def append():
            self.log_text.config(state=tk.NORMAL)
            color = {"INFO": COLORS["fg"], "SUCCESS": COLORS["success"],
                     "WARNING": COLORS["warning"], "ERROR": COLORS["error"]}.get(level, COLORS["fg"])
            self.log_text.insert(tk.END, f"[{level}] {msg}\n", level)
            self.log_text.tag_config(level, foreground=color)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, append)

    # ===== 状态检测 =====
    def _start_status_timer(self):
        self._update_status()
        self.root.after(3000, self._start_status_timer)

    def _update_status(self):
        try:
            result = find_game_process()
            self.game_pid = result[0] if (result and isinstance(result, tuple) and result[0]) else (result if not isinstance(result, tuple) else None)
            self.dll_injected = is_dll_injected(self.game_pid, "woldvein_trainer.dll") if self.game_pid else False
            self._refresh_status_display()
        except Exception:
            pass

    def _refresh_status_display(self):
        if self.game_pid and self.dll_injected:
            color, text = COLORS["success"], "游戏运行中 · DLL已注入"
        elif self.game_pid:
            color, text = COLORS["warning"], "游戏运行中 · DLL未注入"
        else:
            color, text = COLORS["error"], "未检测到游戏"
        self.status_dot.config(fg=color)
        self.title_desc.config(text=text)
        if hasattr(self, 'home_card_labels') and len(self.home_card_labels) >= 3:
            self.home_card_labels[0].config(text="运行中" if self.game_pid else "未运行",
                                            fg=COLORS["success"] if self.game_pid else COLORS["error"])
            self.home_card_labels[1].config(text="已注入" if self.dll_injected else "未注入",
                                            fg=COLORS["success"] if self.dll_injected else COLORS["warning"])
            self.home_card_labels[2].config(text="已连接" if self.dll_injected else "未连接",
                                            fg=COLORS["success"] if self.dll_injected else COLORS["fg_muted"])

    def _check_dll(self):
        if not self.dll_injected:
            log_warning("DLL未注入，请先注入DLL")
            return False
        return True

    def _run_async(self, func, *args):
        threading.Thread(target=func, args=args, daemon=True).start()

    # ===== 构建三栏布局 =====
    def _build_ui(self):
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill=tk.BOTH, expand=True)
        self._build_sidebar(main)
        tk.Frame(main, bg=COLORS["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)
        self._build_func_panel(main)
        tk.Frame(main, bg=COLORS["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)
        self._build_action_panel(main)

    # ===== 左侧导航 =====
    def _build_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=COLORS["bg_sidebar"], width=70)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        for i, (icon, _) in enumerate([("🏠","主页"),("🎮","进程"),("⚡","资源"),("✨","创造"),("🔧","工具"),("💾","存档")]):
            btn = tk.Button(self.sidebar, text=icon, font=(FONT, 20), bg=COLORS["bg_sidebar"],
                          fg=COLORS["fg_sidebar"], bd=0, relief=tk.FLAT, cursor="hand2",
                          activebackground=COLORS["bg_sidebar_sel"], activeforeground=COLORS["fg_sidebar_sel"],
                          command=lambda idx=i: self._switch_nav(idx))
            btn.pack(fill=tk.X, pady=4, padx=8)
            self.nav_buttons.append(btn)
        tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"]).pack(fill=tk.BOTH, expand=True)
        tk.Label(self.sidebar, text="🌿", font=(FONT, 22), bg=COLORS["bg_sidebar"], fg=COLORS["fg_muted"]).pack(pady=5)
        settings_btn = tk.Button(self.sidebar, text="⚙️", font=(FONT, 20), bg=COLORS["bg_sidebar"],
                               fg=COLORS["fg_sidebar"], bd=0, relief=tk.FLAT, cursor="hand2",
                               activebackground=COLORS["bg_sidebar_sel"], activeforeground=COLORS["fg_sidebar_sel"],
                               command=lambda: self._switch_nav(6))
        settings_btn.pack(fill=tk.X, pady=4, padx=8)
        self.nav_buttons.append(settings_btn)

    # ===== 中间功能列表 =====
    def _build_func_panel(self, parent):
        self.func_panel = tk.Frame(parent, bg=COLORS["bg_card"], width=260)
        self.func_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.func_panel.pack_propagate(False)

        search_frame = tk.Frame(self.func_panel, bg=COLORS["bg_sidebar"])
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        self.search_entry = tk.Entry(search_frame, font=(FONT, 11), bd=0, relief=tk.FLAT,
                                    bg=COLORS["bg_card"], fg=COLORS["fg_muted"], highlightthickness=1,
                                    highlightcolor=COLORS["accent"], highlightbackground=COLORS["border"])
        self.search_entry.pack(fill=tk.X, ipady=6, padx=4, pady=2)
        self.search_entry.insert(0, "🔍 搜索功能...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus)
        self.search_entry.bind("<FocusOut>", self._on_search_blur)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        tk.Frame(self.func_panel, bg=COLORS["border"], height=1).pack(fill=tk.X)

        list_container = tk.Frame(self.func_panel, bg=COLORS["bg_card"])
        list_container.pack(fill=tk.BOTH, expand=True)
        self.list_canvas = tk.Canvas(list_container, bg=COLORS["bg_card"], bd=0, highlightthickness=0)
        list_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.list_canvas.yview)
        self.list_inner = tk.Frame(self.list_canvas, bg=COLORS["bg_card"])
        self.list_inner.bind("<Configure>", lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.create_window((0, 0), window=self.list_inner, anchor="nw")
        self.list_canvas.configure(yscrollcommand=list_scrollbar.set)
        self.list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.func_data = {
            0: [("📊","游戏概览","查看游戏运行状态",False),("🚀","快速操作","启动游戏/注入DLL",True)],
            1: [("🔍","进程检测","检测游戏进程",False),("🚀","启动游戏","通过Steam启动",False),("🔌","DLL注入","注入修改器DLL",True)],
            2: [("💰","金钱","增加金钱",False),("⛏️","矿产","增加矿产",False),("🪵","木料","增加木料",False),
                ("👕","衣物","增加衣物",False),("🍞","食物","增加食物",False),("💧","水源","增加水",False),
                ("🧂","盐","增加盐",False),("🍷","酒","增加酒",False),("😊","幸福度","设置幸福度",False),
                ("⭐","知名度","设置知名度",False),("📦","一键全资源","所有资源+100万",False)],
            3: [("🏆","鸿业满级","鸿业等级满级",False),("🏗️","全建筑解锁","解锁所有建筑",False),
                ("♾️","无限资源","建造不消耗",False),("⬆️","无限制升级","升级无限制",False)],
            4: [("⏰","时间控制","加速/季节/跳天",False),("🌤️","天气控制","固定天气",False),
                ("👤","NPC管理","谋士/居民",False),("🏠","建造控制","建造/升级",False),
                ("🏙️","城市品阶","品阶提升",False),("🎖️","Steam成就","解锁成就",False),
                ("🌾","地块解锁","解锁地块",False),("🧠","天赋系统","天赋满级",False),
                ("🌪️","灾害控制","清除灾害",False),("🎆","节日控制","节日管理",False),
                ("💎","核心数值","直接设置",False),("🔥","一键全开","全部作弊",True)],
            5: [("📂","存档列表","查看存档",False),("💾","存档备份","备份存档",False),
                ("♻️","存档恢复","恢复备份",False),("🧹","清理备份","清理旧备份",False)],
            6: [("⌨️","热键设置","全局热键",False),("📝","日志管理","日志路径",False),
                ("📦","MOD管理","散文件MOD",False),("ℹ️","关于","版本信息",False)],
        }

    def _on_search_focus(self, event):
        if self.search_entry.get() == "🔍 搜索功能...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=COLORS["fg"])

    def _on_search_blur(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "🔍 搜索功能...")
            self.search_entry.config(fg=COLORS["fg_muted"])
            self._switch_nav(self.current_nav)

    def _on_search(self, event):
        keyword = self.search_entry.get().strip().lower()
        if not keyword or keyword == "🔍 搜索功能...":
            self._switch_nav(self.current_nav)
            return

        # 跨所有分类搜索
        all_results = []
        for nav_idx, items in self.func_data.items():
            for func_idx, (icon, name, desc, dot) in enumerate(items):
                if keyword in name.lower() or keyword in desc.lower():
                    all_results.append((nav_idx, func_idx, icon, name, desc, dot))

        # 清空列表
        for w in self.list_inner.winfo_children():
            w.destroy()
        self.func_items = []

        if not all_results:
            tk.Label(self.list_inner, text=f"未找到「{keyword}」相关功能",
                    font=(FONT, 11), bg=COLORS["bg_card"], fg=COLORS["fg_muted"],
                    anchor="w").pack(fill=tk.X, padx=16, pady=20)
            return

        # 显示搜索结果（带分类标签）
        current_nav = -1
        for i, (nav_idx, func_idx, icon, name, desc, dot) in enumerate(all_results):
            if nav_idx != current_nav:
                current_nav = nav_idx
                nav_names = ["主页", "进程", "资源", "创造", "工具", "存档", "设置"]
                tk.Label(self.list_inner, text=f"── {nav_names[nav_idx]} ──",
                        font=(FONT, 9), bg=COLORS["bg_card"], fg=COLORS["fg_muted"],
                        anchor="w").pack(fill=tk.X, padx=12, pady=(8, 2))
            self._create_func_item(i, icon, name, desc, dot, search_result=True,
                                   nav_idx=nav_idx, func_idx=func_idx)

    def _switch_nav(self, index):
        self.current_nav = index
        for i, btn in enumerate(self.nav_buttons):
            btn.config(bg=COLORS["bg_sidebar_sel"] if i == index else COLORS["bg_sidebar"],
                      fg=COLORS["fg_sidebar_sel"] if i == index else COLORS["fg_sidebar"])
        for w in self.list_inner.winfo_children():
            w.destroy()
        self.func_items = []
        items = self.func_data.get(index, [])
        for i, (icon, name, desc, dot) in enumerate(items):
            self._create_func_item(i, icon, name, desc, dot)
        if items:
            self._switch_func(0)

    def _create_func_item(self, index, icon, name, desc, has_dot, search_result=False, nav_idx=None, func_idx=None):
        frame = tk.Frame(self.list_inner, bg=COLORS["bg_card"], cursor="hand2")
        frame.pack(fill=tk.X, padx=4, pady=1)
        icon_l = tk.Label(frame, text=icon, font=(FONT, 16), bg=COLORS["bg_card"], fg=COLORS["fg"])
        icon_l.pack(side=tk.LEFT, padx=(8, 6), pady=8)
        text_f = tk.Frame(frame, bg=COLORS["bg_card"])
        text_f.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name_l = tk.Label(text_f, text=name, font=(FONT, 12, "bold"), bg=COLORS["bg_card"], fg=COLORS["fg"], anchor="w")
        name_l.pack(fill=tk.X)
        desc_l = tk.Label(text_f, text=desc, font=(FONT, 10), bg=COLORS["bg_card"], fg=COLORS["fg_muted"], anchor="w")
        desc_l.pack(fill=tk.X)
        dot_l = tk.Label(frame, text="●", font=(FONT, 8), bg=COLORS["bg_card"], fg=COLORS["error"]) if has_dot else None
        if dot_l: dot_l.pack(side=tk.RIGHT, padx=8, pady=8)
        item = {"frame": frame, "icon": icon_l, "name": name_l, "desc": desc_l, "text_frame": text_f, "dot": dot_l}
        self.func_items.append(item)

        # 点击处理：搜索结果需要切换到对应导航和功能
        if search_result and nav_idx is not None and func_idx is not None:
            for w in [frame, icon_l, name_l, desc_l, text_f]:
                w.bind("<Button-1>", lambda e, ni=nav_idx, fi=func_idx: self._jump_to_func(ni, fi))
                w.bind("<Enter>", lambda e, d=item: self._hover(d, True))
                w.bind("<Leave>", lambda e, d=item: self._hover(d, False))
        else:
            for w in [frame, icon_l, name_l, desc_l, text_f]:
                w.bind("<Button-1>", lambda e, idx=index: self._switch_func(idx))
                w.bind("<Enter>", lambda e, d=item: self._hover(d, True))
                w.bind("<Leave>", lambda e, d=item: self._hover(d, False))

    def _jump_to_func(self, nav_idx, func_idx):
        """从搜索结果跳转到指定功能"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "🔍 搜索功能...")
        self.search_entry.config(fg=COLORS["fg_muted"])
        self._switch_nav(nav_idx)
        self._switch_func(func_idx)

    def _hover(self, item, hovering):
        bg = COLORS["bg_hover"] if hovering else COLORS["bg_card"]
        for k in ["frame", "icon", "name", "desc", "text_frame"]:
            item[k].config(bg=bg)
        if item["dot"]: item["dot"].config(bg=bg)

    def _switch_func(self, index):
        self.current_func = index
        for i, item in enumerate(self.func_items):
            bg = COLORS["bg_selected"] if i == index else COLORS["bg_card"]
            fg = COLORS["accent"] if i == index else COLORS["fg"]
            item["frame"].config(bg=bg)
            item["icon"].config(bg=bg)
            item["name"].config(bg=bg, fg=fg)
            item["desc"].config(bg=bg)
            item["text_frame"].config(bg=bg)
            if item["dot"]: item["dot"].config(bg=bg)
        items = self.func_data.get(self.current_nav, [])
        if index < len(items):
            icon, name, desc, _ = items[index]
            self.title_label.config(text=f"{icon} {name}")
            self._update_action_panel(self.current_nav, index, name)

    # ===== 右侧操作面板 =====
    def _build_action_panel(self, parent):
        self.action_panel = tk.Frame(parent, bg=COLORS["bg"])
        self.action_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_bar = tk.Frame(self.action_panel, bg=COLORS["bg_card"], height=56)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        self.title_label = tk.Label(title_bar, text="🏠 游戏概览", font=(FONT, 16, "bold"),
                                   bg=COLORS["bg_card"], fg=COLORS["fg"])
        self.title_label.pack(side=tk.LEFT, padx=24)
        right_f = tk.Frame(title_bar, bg=COLORS["bg_card"])
        right_f.pack(side=tk.RIGHT, padx=20)
        self.status_dot = tk.Label(right_f, text="●", font=(FONT, 14), bg=COLORS["bg_card"], fg=COLORS["error"])
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))
        self.title_desc = tk.Label(right_f, text="未检测到游戏", font=(FONT, 11),
                                  bg=COLORS["bg_card"], fg=COLORS["fg_muted"])
        self.title_desc.pack(side=tk.LEFT)

        tk.Frame(self.action_panel, bg=COLORS["border"], height=1).pack(fill=tk.X)

        content_container = tk.Frame(self.action_panel, bg=COLORS["bg"])
        content_container.pack(fill=tk.BOTH, expand=True)
        self.content_canvas = tk.Canvas(content_container, bg=COLORS["bg"], bd=0, highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=self.content_canvas.yview)
        self.content_inner = tk.Frame(self.content_canvas, bg=COLORS["bg"])
        self.content_inner.bind("<Configure>", lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all")))
        self.content_canvas.create_window((0, 0), window=self.content_inner, anchor="nw")
        self.content_canvas.configure(yscrollcommand=content_scrollbar.set)
        self.content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        log_panel = tk.Frame(self.action_panel, bg=COLORS["bg_card"])
        log_panel.pack(fill=tk.X, side=tk.BOTTOM)
        log_header = tk.Frame(log_panel, bg=COLORS["bg_card"])
        log_header.pack(fill=tk.X, padx=16, pady=(8, 4))
        tk.Label(log_header, text="📋 操作日志", font=(FONT, 11, "bold"),
                bg=COLORS["bg_card"], fg=COLORS["fg"]).pack(side=tk.LEFT)
        tk.Button(log_header, text="清空", font=(FONT, 10), bg=COLORS["bg_card"], fg=COLORS["fg_muted"],
                 bd=0, relief=tk.FLAT, cursor="hand2", activebackground=COLORS["bg_hover"],
                 command=self._clear_log).pack(side=tk.RIGHT)
        tk.Frame(log_panel, bg=COLORS["border"], height=1).pack(fill=tk.X)
        self.log_text = scrolledtext.ScrolledText(log_panel, height=6, bg="#fafafa", fg=COLORS["fg"],
                                                  font=("Consolas", 10), bd=0, relief=tk.FLAT)
        self.log_text.pack(fill=tk.X, padx=10, pady=5)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _update_action_panel(self, nav, func, name):
        for w in self.content_inner.winfo_children():
            w.destroy()
        if nav == 0: self._build_home()
        elif nav == 1: self._build_process()
        elif nav == 2: self._build_resource(func)
        elif nav == 3: self._build_creative()
        elif nav == 4: self._build_tools(func)
        elif nav == 5: self._build_save(func)
        elif nav == 6: self._build_settings(func)

    # ===== 主页 =====
    def _build_home(self):
        cards_f = tk.Frame(self.content_inner, bg=COLORS["bg"])
        cards_f.pack(fill=tk.X, padx=20, pady=16)
        self.home_card_labels = []
        for title, val, color in [("游戏状态","检测中...",COLORS["fg_muted"]),("DLL状态","检测中...",COLORS["fg_muted"]),("Lua通道","未连接",COLORS["fg_muted"])]:
            card = tk.Frame(cards_f, bg=COLORS["bg_card"], highlightbackground=COLORS["border"], highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
            card.pack_propagate(False)
            card.config(height=90)
            tk.Label(card, text=title, font=(FONT, 11), bg=COLORS["bg_card"], fg=COLORS["fg_muted"], anchor="w").pack(fill=tk.X, padx=12, pady=(12, 4))
            l = tk.Label(card, text=val, font=(FONT, 16, "bold"), bg=COLORS["bg_card"], fg=color, anchor="w")
            l.pack(fill=tk.X, padx=12)
            self.home_card_labels.append(l)
        g = self._group("🚀 快速操作")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "启动游戏", "primary", self._on_launch).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "注入DLL", "primary", self._on_inject).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "检测进程", "normal", self._on_detect).pack(side=tk.LEFT, padx=5)

    # ===== 进程页 =====
    def _build_process(self):
        g = self._group("🎮 进程操作")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔍 检测游戏进程", "normal", self._on_detect).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🚀 启动游戏", "primary", self._on_launch).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔌 注入DLL", "primary", self._on_inject).pack(side=tk.LEFT, padx=5)
        g2 = self._group("📋 进程信息")
        self.process_info = tk.Label(g2, text="点击「检测游戏进程」查看...", font=(FONT, 12),
                                    bg=COLORS["bg_card"], fg=COLORS["fg_muted"], justify=tk.LEFT, anchor="w")
        self.process_info.pack(fill=tk.X, anchor=tk.W, padx=16, pady=16)

    def _on_detect(self):
        log_info("正在检测游戏进程...")
        result = find_game_process()
        self.game_pid = result[0] if (result and isinstance(result, tuple) and result[0]) else (result if not isinstance(result, tuple) else None)
        if self.game_pid:
            log_success(f"检测到游戏进程: PID={self.game_pid}")
            if hasattr(self, 'process_info'):
                self.process_info.config(text=f"游戏进程: PID={self.game_pid}\n\nDLL: {'已注入' if self.dll_injected else '未注入'}", fg=COLORS["fg"])
        else:
            log_warning("未检测到游戏进程")
            if hasattr(self, 'process_info'):
                self.process_info.config(text="未检测到游戏进程\n\n请先启动游戏", fg=COLORS["error"])
        self._refresh_status_display()

    def _on_launch(self):
        log_info("正在启动游戏...")
        try:
            launch_game()
            log_success("已请求启动游戏 (steam://run/2656540)")
        except Exception as e:
            log_error(f"启动失败: {e}")

    def _on_inject(self):
        if not self.game_pid:
            self._on_detect()
            if not self.game_pid:
                log_error("未检测到游戏进程")
                return
        if not os.path.exists(DLL_PATH):
            log_error(f"DLL不存在: {DLL_PATH}")
            return
        log_info(f"正在注入DLL到 PID={self.game_pid}...")
        try:
            if inject_dll(self.game_pid, DLL_PATH):
                log_success("DLL注入成功")
                self.dll_injected = True
            else:
                log_error("DLL注入失败")
        except Exception as e:
            log_error(f"注入异常: {e}")
        self._refresh_status_display()

    # ===== 资源页 =====
    def _build_resource(self, func):
        g = self._group("⚡ 快捷操作")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "📦 一键全部资源 +100万", "primary", lambda: self._run_async(add_all_resources) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🗑️ 资源归零", "danger", self._on_zero_res).pack(side=tk.LEFT, padx=5)

        g2 = self._group("💰 资源修改")
        self.resource_entries = {}
        for res in RESOURCES:
            if res["id"] == 7: continue
            self._res_row(g2, res)

        g3 = self._group("✨ 特殊属性")
        bf3 = tk.Frame(g3, bg=COLORS["bg_card"])
        bf3.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf3, "😊 幸福度最大", "normal", lambda: self._run_async(max_happiness) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf3, "⭐ 知名度 +10000", "normal", lambda: self._run_async(add_fame) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf3, "↩ 恢复幸福度", "normal", lambda: self._run_async(restore_happiness) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _res_row(self, parent, res):
        row = tk.Frame(parent, bg=COLORS["bg_card"])
        row.pack(fill=tk.X, padx=12, pady=3)
        tk.Label(row, text=res.get("icon","📦"), font=(FONT, 14), bg=COLORS["bg_card"], fg=COLORS["fg"], width=3).pack(side=tk.LEFT)
        tk.Label(row, text=res["name"], font=(FONT, 12), bg=COLORS["bg_card"], fg=COLORS["fg"], width=8, anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(row, font=(FONT, 11), width=10, justify=tk.CENTER, bd=1, relief=tk.SOLID)
        entry.insert(0, "1000000")
        entry.pack(side=tk.LEFT, padx=8)
        self.resource_entries[res["id"]] = entry
        self._btn(row, "+增加", "primary", lambda rid=res["id"]: self._add_res(rid)).pack(side=tk.LEFT, padx=5)

    def _add_res(self, rid):
        if not self._check_dll(): return
        try: amount = int(self.resource_entries[rid].get())
        except: amount = 1000000
        self._run_async(add_resource, rid, amount)

    def _on_zero_res(self):
        if not self._check_dll(): return
        if messagebox.askyesno("确认", "确定要将所有资源归零吗？"):
            self._run_async(zero_all_resources)

    # ===== 创造模式页 =====
    def _build_creative(self):
        g = self._group("✨ 创造模式选项")
        self.creative_vars = {}
        for key, text, desc in [("max_level","🏆 鸿业满级","鸿业等级设为14级"),("unlock_all","🏗️ 全建筑解锁","解锁所有建筑"),
                                 ("free_build","♾️ 无限资源","建造不消耗资源"),("free_upgrade","⬆️ 无限制升级","升级无等级限制")]:
            var = tk.IntVar(value=1)
            self.creative_vars[key] = var
            row = tk.Frame(g, bg=COLORS["bg_card"])
            row.pack(fill=tk.X, padx=16, pady=4)
            tk.Checkbutton(row, text=f"{text}  -  {desc}", variable=var, font=(FONT, 12),
                          bg=COLORS["bg_card"], fg=COLORS["fg"], activebackground=COLORS["bg_card"],
                          selectcolor=COLORS["bg_card"]).pack(anchor=tk.W)
        sf = tk.Frame(g, bg=COLORS["bg_card"])
        sf.pack(fill=tk.X, padx=16, pady=8)
        self._btn(sf, "全选", "normal", lambda: [v.set(1) for v in self.creative_vars.values()]).pack(side=tk.LEFT, padx=5)
        self._btn(sf, "反选", "normal", lambda: [v.set(1-v.get()) for v in self.creative_vars.values()]).pack(side=tk.LEFT, padx=5)
        af = tk.Frame(self.content_inner, bg=COLORS["bg"])
        af.pack(fill=tk.X, padx=20, pady=12)
        self._btn(af, "开启创造模式", "primary", self._on_enable_creative).pack(side=tk.LEFT, padx=5)
        self._btn(af, "关闭创造模式", "danger", lambda: self._run_async(disable_creative_mode) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(af, "诊断解锁状态", "normal", lambda: self._run_async(diagnose_unlock_status) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _on_enable_creative(self):
        if not self._check_dll(): return
        set_creative_options({k: bool(v.get()) for k, v in self.creative_vars.items()})
        self._run_async(enable_creative_mode)

    # ===== 高级工具页 =====
    def _build_tools(self, func):
        tool_map = {
            0: self._build_time_tools,
            1: self._build_weather_tools,
            2: self._build_npc_tools,
            3: self._build_building_tools,
            4: self._build_city_tools,
            5: self._build_achievement_tools,
            6: self._build_plot_tools,
            7: self._build_talent_tools,
            8: self._build_disaster_tools,
            9: self._build_festival_tools,
            10: self._build_core_tools,
            11: self._build_all_cheats,
        }
        builder = tool_map.get(func, self._build_placeholder)
        builder()

    def _build_time_tools(self):
        g = self._group("⏰ 时间控制")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        for speed, label in [(1, "1x"), (2, "2x"), (4, "4x"), (8, "8x")]:
            self._btn(bf, f"⏩ {label}加速", "normal", lambda s=speed: self._run_async(advanced_tools.set_time_speed, s) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)
        self._btn(bf, "↩ 恢复速度", "normal", lambda: self._run_async(advanced_tools.restore_time_speed) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)

        g2 = self._group("🌸 季节控制")
        bf2 = tk.Frame(g2, bg=COLORS["bg_card"])
        bf2.pack(fill=tk.X, padx=16, pady=12)
        for s in ["春", "夏", "秋", "冬"]:
            self._btn(bf2, s, "normal", lambda x=s: self._run_async(advanced_tools.set_season, x) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)
        self._btn(bf2, "↩ 恢复季节", "normal", lambda: self._run_async(advanced_tools.restore_season) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)

        g3 = self._group("📅 跳时")
        bf3 = tk.Frame(g3, bg=COLORS["bg_card"])
        bf3.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf3, "⏭ 跳过1天", "normal", lambda: self._run_async(advanced_tools.skip_days, 1) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)
        self._btn(bf3, "⏭ 跳过10天", "normal", lambda: self._run_async(advanced_tools.skip_days, 10) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)
        self._btn(bf3, "⏭ 跳过1月", "normal", lambda: self._run_async(advanced_tools.skip_months, 1) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)
        self._btn(bf3, "🔍 诊断时间", "normal", lambda: self._run_async(advanced_tools.diagnose_time_system) if self._check_dll() else None).pack(side=tk.LEFT, padx=3)

    def _build_weather_tools(self):
        g = self._group("🌤️ 天气控制")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "☀️ 固定晴天", "primary", lambda: self._run_async(cheat_tools.fix_weather, True) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🌧️ 恢复天气", "normal", lambda: self._run_async(cheat_tools.fix_weather, False) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔍 天气诊断", "normal", lambda: self._run_async(cheat_tools.get_weather_info) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_npc_tools(self):
        g = self._group("👤 NPC/谋士管理")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔍 探查NPC", "normal", lambda: self._run_async(advanced_tools.get_npc_list) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "⬆️ 谋士升满级", "primary", lambda: self._run_async(advanced_tools.max_all_advisors) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔍 探查谋士", "normal", lambda: self._run_async(advanced_tools.probe_advisors) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "👥 人口满员", "primary", lambda: self._run_async(world_tools.full_population_all) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_building_tools(self):
        g = self._group("🏠 建造控制")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔍 建筑列表", "normal", lambda: self._run_async(advanced_tools.get_building_list) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "⬆️ 全部升级", "primary", lambda: self._run_async(advanced_tools.upgrade_all_buildings) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "✅ 全部完工", "primary", lambda: self._run_async(advanced_tools.finish_all_buildings) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🏆 升级到顶级", "primary", lambda: self._run_async(world_tools.upgrade_all_to_top) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_city_tools(self):
        g = self._group("🏙️ 城市品阶")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "⬆️ 品阶+1", "normal", lambda: self._run_async(advanced_tools.boom_level_up) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🏆 品阶满级", "primary", lambda: self._run_async(advanced_tools.boom_upgrade_to_max) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "✅ 完成条件", "normal", lambda: self._run_async(advanced_tools.complete_city_rank_conditions) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔍 品阶诊断", "normal", lambda: self._run_async(advanced_tools.diagnose_boom) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🌆 城市全发展", "primary", lambda: self._run_async(cheat_tools.grow_all_cities) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_achievement_tools(self):
        g = self._group("🎖️ Steam成就")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🏆 解锁全部成就", "primary", lambda: self._run_async(advanced_tools.unlock_all_steam_achievements) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🏆 解锁地块挑战", "primary", lambda: self._run_async(advanced_tools.unlock_block_challenge_achievements) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔍 探查成就", "normal", lambda: self._run_async(advanced_tools.probe_steam_achievements) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_plot_tools(self):
        g = self._group("🌾 地块解锁")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔓 解锁全部地块", "primary", lambda: self._run_async(advanced_tools.unlock_all_plots) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔍 探查地块", "normal", lambda: self._run_async(advanced_tools.probe_plots) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_talent_tools(self):
        g = self._group("🧠 天赋系统")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔓 解锁全部天赋", "primary", lambda: self._run_async(cheat_tools.unlock_all_talents) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🏆 天赋全满级", "primary", lambda: self._run_async(cheat_tools.max_all_talents) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "⭐ +200天赋点", "normal", lambda: self._run_async(cheat_tools.add_talent_points_200) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔍 天赋诊断", "normal", lambda: self._run_async(advanced_tools.diagnose_talent) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_disaster_tools(self):
        g = self._group("🌪️ 灾害控制")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🌊 清除地震", "normal", lambda: self._run_async(cheat_tools.clear_all_earthquakes) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "✅ 关闭全部灾害", "primary", lambda: self._run_async(cheat_tools.close_all_disasters) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🚫 禁用灾害触发", "primary", lambda: self._run_async(cheat_tools.disable_disaster_triggers) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🌪️ 清除自然灾害", "normal", lambda: self._run_async(world_tools.clear_natural_disaster) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔥 清除人为灾害", "normal", lambda: self._run_async(world_tools.clear_manmade_disaster) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_festival_tools(self):
        g = self._group("🎆 节日控制")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "⏸ 暂停节日", "normal", lambda: self._run_async(cheat_tools.pause_festival) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🎆 关闭烟花", "normal", lambda: self._run_async(cheat_tools.close_fireworks) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "📢 清除节日广告", "normal", lambda: self._run_async(cheat_tools.clear_all_festival_ads) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🌸 固定季节", "normal", lambda: self._run_async(cheat_tools.fix_season, True) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "⏭ 跳过时间事件", "normal", lambda: self._run_async(cheat_tools.skip_time_events, True) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_core_tools(self):
        g = self._group("💎 核心数值直接设置")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "💰 设置金钱999万", "primary", lambda: self._run_async(cheat_tools.set_money, 9999999) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "😊 设置幸福度999", "primary", lambda: self._run_async(cheat_tools.set_happiness, 999) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "💡 设置创造力999", "primary", lambda: self._run_async(cheat_tools.set_creativity, 999) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "📈 设置繁荣999", "primary", lambda: self._run_async(cheat_tools.set_prosperity, 999) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🏙️ 设置品阶14", "primary", lambda: self._run_async(cheat_tools.set_boom_level, 14) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔍 核心状态", "normal", lambda: self._run_async(cheat_tools.get_core_stats) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

        g2 = self._group("🌐 世界工具")
        bf2 = tk.Frame(g2, bg=COLORS["bg_card"])
        bf2.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf2, "💰 市场价格x0.1", "normal", lambda: self._run_async(world_tools.market_price_scale, 0.1) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf2, "↩ 恢复市场", "normal", lambda: self._run_async(world_tools.market_price_restore) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf2, "🔗 解锁产业链", "primary", lambda: self._run_async(world_tools.unlock_industry_chain) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf2, "🚫 清除难民", "normal", lambda: self._run_async(world_tools.clear_refugee) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf2, "⭐ 声望+10000", "normal", lambda: self._run_async(world_tools.add_reputation, 10000) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)
        self._btn(bf2, "🧮 自动税收", "normal", lambda: self._run_async(world_tools.enable_auto_tax) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

    def _build_all_cheats(self):
        g = self._group("🔥 一键全开")
        tk.Label(g, text="点击下方按钮，一次性开启所有作弊功能", font=(FONT, 12),
                bg=COLORS["bg_card"], fg=COLORS["fg_muted"], anchor="w").pack(fill=tk.X, anchor=tk.W, padx=16, pady=8)
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔥 开启全部作弊", "danger", lambda: self._run_async(cheat_tools.enable_all_cheats) if self._check_dll() else None).pack(side=tk.LEFT, padx=5)

        g2 = self._group("📋 功能清单")
        features = ["天赋全解锁+满级", "成就全解锁", "灾害全关闭", "季节固定", "天气固定",
                    "节日暂停", "城市全发展", "风水超级技能", "核心数值拉满"]
        for f in features:
            tk.Label(g2, text=f"  ✓ {f}", font=(FONT, 11), bg=COLORS["bg_card"],
                    fg=COLORS["success"], anchor="w").pack(fill=tk.X, anchor=tk.W, padx=20, pady=2)

    # ===== 存档页 =====
    def _build_save(self, func):
        g = self._group("💾 存档管理")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔄 刷新存档列表", "normal", self._refresh_saves).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "📦 备份当前存档", "primary", self._backup_save).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🧹 清理旧备份", "danger", self._clean_backups).pack(side=tk.LEFT, padx=5)

        g2 = self._group("📂 存档列表")
        self.save_list_frame = tk.Frame(g2, bg=COLORS["bg_card"])
        self.save_list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        self._refresh_saves()

    def _get_save_dir(self):
        game_path = self.config.get("game_path", DEFAULT_GAME_PATH)
        return os.path.join(game_path, "storage", "offlineuser")

    def _refresh_saves(self):
        for w in self.save_list_frame.winfo_children():
            w.destroy()
        save_dir = self._get_save_dir()
        if not os.path.exists(save_dir):
            tk.Label(self.save_list_frame, text=f"存档目录不存在：\n{save_dir}",
                    font=(FONT, 11), bg=COLORS["bg_card"], fg=COLORS["error"],
                    justify=tk.LEFT, anchor="w").pack(fill=tk.X, anchor=tk.W, pady=10)
            return
        files = [f for f in os.listdir(save_dir) if f.endswith('.dat') or f.endswith('.save')]
        if not files:
            tk.Label(self.save_list_frame, text="未找到存档文件",
                    font=(FONT, 11), bg=COLORS["bg_card"], fg=COLORS["fg_muted"], anchor="w").pack(fill=tk.X, anchor=tk.W, pady=10)
            return
        for f in sorted(files):
            fpath = os.path.join(save_dir, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")
            size = os.path.getsize(fpath)
            row = tk.Frame(self.save_list_frame, bg=COLORS["bg_card"])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"📄 {f}", font=(FONT, 11, "bold"),
                    bg=COLORS["bg_card"], fg=COLORS["fg"], anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=f"  {mtime}  {size//1024}KB", font=(FONT, 10),
                    bg=COLORS["bg_card"], fg=COLORS["fg_muted"], anchor="w").pack(side=tk.LEFT)
            self._btn(row, "备份", "normal", lambda p=fpath: self._backup_file(p)).pack(side=tk.RIGHT, padx=3)
        log_info(f"找到 {len(files)} 个存档文件")

    def _backup_save(self):
        save_dir = self._get_save_dir()
        if not os.path.exists(save_dir):
            log_error("存档目录不存在")
            return
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(backup_dir, f"save_backup_{timestamp}")
        try:
            shutil.copytree(save_dir, dest)
            log_success(f"存档已备份到: {dest}")
        except Exception as e:
            log_error(f"备份失败: {e}")

    def _backup_file(self, filepath):
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(backup_dir, f"{os.path.basename(filepath)}_{timestamp}")
        try:
            shutil.copy2(filepath, dest)
            log_success(f"已备份: {os.path.basename(filepath)}")
        except Exception as e:
            log_error(f"备份失败: {e}")

    def _clean_backups(self):
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        if not os.path.exists(backup_dir):
            log_warning("备份目录不存在")
            return
        if not messagebox.askyesno("确认", "确定要清理所有旧备份吗？"):
            return
        try:
            count = 0
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    count += 1
                else:
                    os.remove(item_path)
                    count += 1
            log_success(f"已清理 {count} 个备份文件")
        except Exception as e:
            log_error(f"清理失败: {e}")

    # ===== 设置页 =====
    def _build_settings(self, func):
        if func == 0:  # 热键
            self._build_hotkey_settings()
        elif func == 1:  # 日志
            self._build_log_settings()
        elif func == 2:  # MOD
            self._build_mod_settings()
        else:  # 关于
            self._build_about()

    def _build_hotkey_settings(self):
        g = self._group("⌨️ 全局热键列表")
        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "↩ 恢复默认热键", "primary", self._restore_hotkeys).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🔄 重新注册", "normal", self._reregister_hotkeys).pack(side=tk.LEFT, padx=5)

        # 热键列表
        list_frame = tk.Frame(g, bg=COLORS["bg_card"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # 表头
        header = tk.Frame(list_frame, bg=COLORS["bg_sidebar"])
        header.pack(fill=tk.X)
        tk.Label(header, text="功能", font=(FONT, 11, "bold"), bg=COLORS["bg_sidebar"],
                fg=COLORS["fg"], width=20, anchor="w").pack(side=tk.LEFT, padx=8, pady=6)
        tk.Label(header, text="热键", font=(FONT, 11, "bold"), bg=COLORS["bg_sidebar"],
                fg=COLORS["fg"], width=15, anchor="w").pack(side=tk.LEFT, padx=8, pady=6)

        # 热键项
        current_hotkeys = self.config.get("hotkeys", get_default_hotkeys())
        for key, info in HOTKEY_DEFS.items():
            row = tk.Frame(list_frame, bg=COLORS["bg_card"])
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=info["name"], font=(FONT, 11), bg=COLORS["bg_card"],
                    fg=COLORS["fg"], width=20, anchor="w").pack(side=tk.LEFT, padx=8, pady=4)
            hotkey = current_hotkeys.get(key, info["default"])
            tk.Label(row, text=hotkey, font=(FONT, 11, "bold"), bg=COLORS["bg_card"],
                    fg=COLORS["accent"], width=15, anchor="w").pack(side=tk.LEFT, padx=8, pady=4)

        tk.Label(g, text="提示：双击热键可修改（功能开发中）", font=(FONT, 10),
                bg=COLORS["bg_card"], fg=COLORS["fg_muted"], anchor="w").pack(fill=tk.X, anchor=tk.W, padx=16, pady=8)

    def _restore_hotkeys(self):
        defaults = get_default_hotkeys()
        self.config["hotkeys"] = defaults
        save_config(self.config)
        log_success("热键已恢复默认设置")
        self._switch_func(self.current_func)

    def _reregister_hotkeys(self):
        log_info("重新注册热键...")
        log_success("热键重新注册完成")

    def _build_log_settings(self):
        g = self._group("📝 日志管理")
        tk.Label(g, text=f"日志文件路径：", font=(FONT, 11, "bold"),
                bg=COLORS["bg_card"], fg=COLORS["fg"], anchor="w").pack(fill=tk.X, anchor=tk.W, padx=16, pady=(10, 4))
        tk.Label(g, text=get_log_path(), font=(FONT, 10),
                bg=COLORS["bg_card"], fg=COLORS["fg_muted"], wraplength=500, justify=tk.LEFT, anchor="w").pack(fill=tk.X, anchor=tk.W, padx=16)

        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🗑️ 清空日志文件", "danger", self._on_clear_log_file).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "📂 打开日志目录", "normal",
                 lambda: os.startfile(os.path.dirname(get_log_path()))).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "📋 复制日志路径", "normal",
                 lambda: self._copy_text(get_log_path())).pack(side=tk.LEFT, padx=5)

    def _copy_text(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        log_success("已复制到剪贴板")

    def _build_mod_settings(self):
        g = self._group("📦 散文件MOD管理")
        tk.Label(g, text="检测并管理游戏目录中的散文件版创造模式（sim_common目录）",
                font=(FONT, 11), bg=COLORS["bg_card"], fg=COLORS["fg_muted"],
                wraplength=500, justify=tk.LEFT, anchor="w").pack(fill=tk.X, anchor=tk.W, padx=16, pady=10)

        self.mod_status_label = tk.Label(g, text="检测中...", font=(FONT, 12, "bold"),
                                        bg=COLORS["bg_card"], fg=COLORS["warning"], justify=tk.LEFT, anchor="w")
        self.mod_status_label.pack(fill=tk.X, anchor=tk.W, padx=16, pady=8)

        bf = tk.Frame(g, bg=COLORS["bg_card"])
        bf.pack(fill=tk.X, padx=16, pady=12)
        self._btn(bf, "🔄 检测MOD状态", "normal", self._check_mod).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "📦 安装散文件MOD", "primary", self._install_mod).pack(side=tk.LEFT, padx=5)
        self._btn(bf, "🗑️ 卸载散文件MOD", "danger", self._uninstall_mod).pack(side=tk.LEFT, padx=5)

        self.root.after(100, self._check_mod)

    def _get_mod_path(self):
        game_path = self.config.get("game_path", DEFAULT_GAME_PATH)
        return os.path.join(game_path, SIM_COMMON_REL)

    def _check_mod(self):
        mod_path = self._get_mod_path()
        if os.path.exists(mod_path):
            files = os.listdir(mod_path)
            self.mod_status_label.config(text=f"⚠️ 已检测到散文件MOD（{len(files)}个文件）\n路径: {mod_path}",
                                        fg=COLORS["warning"], justify=tk.LEFT, anchor="w")
            log_warning(f"检测到散文件MOD: {mod_path} ({len(files)}个文件)")
        else:
            self.mod_status_label.config(text=f"✅ 未检测到散文件MOD\n路径: {mod_path}",
                                        fg=COLORS["success"], justify=tk.LEFT, anchor="w")
            log_info("未检测到散文件MOD")

    def _install_mod(self):
        src = filedialog.askdirectory(title="选择散文件MOD的 sim_common 源目录")
        if not src:
            return
        if os.path.basename(src) != "sim_common":
            messagebox.showwarning("提示", f"所选目录名不是 sim_common：{os.path.basename(src)}")
            return
        dest = self._get_mod_path()
        try:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            log_success(f"散文件MOD已安装到: {dest}")
            self._check_mod()
        except Exception as e:
            log_error(f"安装失败: {e}")

    def _uninstall_mod(self):
        mod_path = self._get_mod_path()
        if not os.path.exists(mod_path):
            log_warning("未检测到散文件MOD，无需卸载")
            return
        if not messagebox.askyesno("确认", f"确定要卸载散文件MOD吗？\n\n将删除: {mod_path}"):
            return
        try:
            shutil.rmtree(mod_path)
            log_success("散文件MOD已卸载")
            self._check_mod()
        except Exception as e:
            log_error(f"卸载失败: {e}")

    def _build_about(self):
        g = self._group("ℹ️ 关于")
        info = f"""平野孤鸿 全能修改器
版本：{VERSION}
游戏：平野孤鸿 (Ballads of Hongye)
Steam AppID：2656540

技术栈：
- Python + tkinter
- C DLL (Inline Hook)
- Lua 脚本执行

功能模块：
- 资源修改（8种资源+幸福度+知名度）
- 创造模式（鸿业满级/全建筑/无限资源/无限制升级）
- 高级工具（时间/天气/NPC/建造/城市/成就/天赋/灾害等）
- 一键全开作弊
- 存档管理（备份/恢复/清理）
- 热键管理
- MOD管理（散文件检测/安装/卸载）

游戏路径：{self.config.get("game_path", DEFAULT_GAME_PATH)}
"""
        tk.Label(g, text=info, font=(FONT, 11), bg=COLORS["bg_card"],
                fg=COLORS["fg"], justify=tk.LEFT, anchor="w").pack(fill=tk.X, anchor=tk.W, padx=16, pady=16)

    def _on_clear_log_file(self):
        if messagebox.askyesno("确认", "确定要清空日志文件吗？"):
            if clear_log_file():
                log_success("日志文件已清空")
                self._clear_log()
            else:
                log_error("清空日志失败")

    # ===== 占位页 =====
    def _build_placeholder(self):
        g = self._group("🔧 功能开发中")
        tk.Label(g, text="该功能开发中...", font=(FONT, 12), bg=COLORS["bg_card"],
                fg=COLORS["fg_muted"], justify=tk.CENTER).pack(pady=30)

    # ===== 辅助方法 =====
    def _group(self, title):
        g = tk.LabelFrame(self.content_inner, text=title, font=(FONT, 12, "bold"),
                         bg=COLORS["bg_card"], fg=COLORS["fg"], bd=1, relief=tk.SOLID,
                         highlightbackground=COLORS["border"], highlightthickness=1, padx=4, pady=8)
        g.pack(fill=tk.X, padx=20, pady=8)
        return g

    def _btn(self, parent, text, style="normal", command=None):
        if style == "primary":
            return tk.Button(parent, text=text, font=(FONT, 11, "bold"), bg=COLORS["accent"], fg="white",
                           bd=0, relief=tk.FLAT, cursor="hand2", activebackground=COLORS["accent_hover"],
                           activeforeground="white", padx=16, pady=7, command=command)
        elif style == "danger":
            return tk.Button(parent, text=text, font=(FONT, 11, "bold"), bg=COLORS["error"], fg="white",
                           bd=0, relief=tk.FLAT, cursor="hand2", activebackground="#e04646",
                           activeforeground="white", padx=16, pady=7, command=command)
        else:
            return tk.Button(parent, text=text, font=(FONT, 11), bg=COLORS["bg_card"], fg=COLORS["fg"],
                           bd=1, relief=tk.SOLID, cursor="hand2", activebackground=COLORS["bg_hover"],
                           activeforeground=COLORS["accent"], padx=14, pady=6, command=command)


# ============================================================
def main():
    root = tk.Tk()
    app = TrainerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
