"""
平野孤鸿修改器 - 独立热键配置工具
功能：独立运行的热键映射配置程序，修改后保存到 config.json，主修改器下次启动时自动加载
用法：python hotkey_configurator.py 或双击 热键配置.bat
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox

# 确保能导入 src 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import load_config, save_config
from src.logger import log, init_log


# 热键功能名称映射
HOTKEY_NAMES = {
    "money": "金钱 +100万",
    "food": "食物 +100万",
    "water": "水 +100万",
    "cloth": "衣物 +100万",
    "wood": "木材 +100万",
    "mineral": "矿物 +100万",
    "salt": "盐 +100万",
    "wine": "酒 +100万",
    "fame": "知名度 +1万",
    "happiness": "幸福度最大",
    "creative_mode": "创造模式开关",
}

# 默认热键
DEFAULT_HOTKEYS = {
    "money": "Ctrl+F1", "food": "Ctrl+F2", "water": "Ctrl+F3",
    "cloth": "Ctrl+F4", "wood": "Ctrl+F5", "mineral": "Ctrl+F6",
    "salt": "Ctrl+F7", "wine": "Ctrl+F8", "fame": "Ctrl+F9",
    "happiness": "Ctrl+F10", "creative_mode": "Ctrl+F12",
}


class HotkeyConfigurator:
    """独立热键配置工具"""

    def __init__(self):
        self.config = load_config()
        self.root = tk.Tk()
        self.root.title("平野孤鸿修改器 - 热键配置")
        self.root.geometry("520x560")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # 主题色
        self.bg = "#1e1e2e"
        self.bg_card = "#313244"
        self.bg_elevated = "#45475a"
        self.fg = "#cdd6f4"
        self.fg_muted = "#a6adc8"
        self.accent = "#89b4fa"
        self.success = "#a6e3a1"
        self.warning = "#f9e2af"
        self.error = "#f38ba8"

        self._setup_styles()
        self._build_ui()
        self._refresh_list()

    def _setup_styles(self):
        """配置ttk样式"""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=self.bg, foreground=self.fg,
                        font=("微软雅黑", 10))
        style.configure("TFrame", background=self.bg)
        style.configure("Card.TFrame", background=self.bg_card)
        style.configure("TLabel", background=self.bg, foreground=self.fg)
        style.configure("Card.TLabel", background=self.bg_card, foreground=self.fg)
        style.configure("Title.TLabel", background=self.bg, foreground=self.fg,
                        font=("微软雅黑", 14, "bold"))
        style.configure("Muted.TLabel", background=self.bg, foreground=self.fg_muted,
                        font=("微软雅黑", 9))
        style.configure("Success.TLabel", background=self.bg_card, foreground=self.success)
        style.configure("Warning.TLabel", background=self.bg_card, foreground=self.warning)
        style.configure("Error.TLabel", background=self.bg_card, foreground=self.error)

        # 按钮
        style.configure("TButton", background=self.bg_elevated, foreground=self.fg,
                        font=("微软雅黑", 10), padding=[12, 6], borderwidth=0)
        style.map("TButton",
                  background=[("active", self.bg_card), ("hover", self.bg_card)])
        style.configure("Primary.TButton", background=self.accent, foreground="#1e1e2e",
                        font=("微软雅黑", 10, "bold"), padding=[14, 7], borderwidth=0)
        style.map("Primary.TButton",
                  background=[("active", "#74c7ec"), ("hover", "#74c7ec")])
        style.configure("Success.TButton", background=self.success, foreground="#1e1e2e",
                        font=("微软雅黑", 10, "bold"), padding=[14, 7], borderwidth=0)
        style.map("Success.TButton",
                  background=[("active", "#94d38f"), ("hover", "#94d38f")])
        style.configure("Danger.TButton", background=self.error, foreground="#1e1e2e",
                        font=("微软雅黑", 10, "bold"), padding=[14, 7], borderwidth=0)
        style.map("Danger.TButton",
                  background=[("active", "#e07088"), ("hover", "#e07088")])
        style.configure("Small.TButton", background=self.bg_elevated, foreground=self.fg,
                        font=("微软雅黑", 9), padding=[8, 4], borderwidth=0)

        # Treeview
        style.configure("Treeview",
                        background=self.bg_card, foreground=self.fg,
                        fieldbackground=self.bg_card, borderwidth=0,
                        rowheight=28, font=("微软雅黑", 10))
        style.configure("Treeview.Heading",
                        background=self.bg_elevated, foreground=self.accent,
                        borderwidth=0, font=("微软雅黑", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", self.bg_elevated)],
                  foreground=[("selected", self.fg)])

        # Checkbutton
        style.configure("TCheckbutton", background=self.bg_card, foreground=self.fg,
                        font=("微软雅黑", 10))
        style.map("TCheckbutton",
                  background=[("active", self.bg_card)])

    def _build_ui(self):
        """构建界面"""
        # 标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 5))
        ttk.Label(title_frame, text="热键配置工具", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_frame, text="v0.3", style="Muted.TLabel").pack(side=tk.LEFT, padx=(8, 0), pady=4)

        # 说明
        ttk.Label(self.root, text="双击热键列可修改，修改后自动保存。主修改器重启后生效。",
                  style="Muted.TLabel").pack(anchor=tk.W, padx=20, pady=(0, 10))

        # 总开关
        switch_frame = ttk.Frame(self.root, style="Card.TFrame")
        switch_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        self.hotkey_enabled_var = tk.BooleanVar(value=self.config.get("hotkeys_enabled", True))
        ttk.Checkbutton(switch_frame, text="启用全局热键", variable=self.hotkey_enabled_var,
                        command=self._on_toggle_enabled).pack(side=tk.LEFT, padx=15, pady=10)
        self.status_label = ttk.Label(switch_frame, text="", style="Card.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)
        self._update_status()

        # 热键列表
        list_frame = ttk.Frame(self.root, style="Card.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # 列表标题栏
        header_frame = ttk.Frame(list_frame, style="Card.TFrame")
        header_frame.pack(fill=tk.X, padx=12, pady=(10, 5))
        ttk.Label(header_frame, text="热键映射", style="Card.TLabel",
                  font=("微软雅黑", 11, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="清空全部", style="Small.TButton",
                   command=self._clear_all).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(header_frame, text="恢复默认", style="Small.TButton",
                   command=self._reset_defaults).pack(side=tk.RIGHT)

        # Treeview
        tree_container = ttk.Frame(list_frame, style="Card.TFrame")
        tree_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        columns = ("function", "key")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=11)
        self.tree.heading("function", text="功能")
        self.tree.heading("key", text="热键（双击修改）")
        self.tree.column("function", width=280, anchor=tk.W)
        self.tree.column("key", width=140, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", self._on_double_click)

        # 底部按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        ttk.Button(btn_frame, text="保存并关闭", style="Primary.TButton",
                   command=self._save_and_close).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="取消", style="TButton",
                   command=self.root.destroy).pack(side=tk.RIGHT, padx=(0, 10))

        # 配置文件路径提示
        config_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "woldvein_trainer", "config.json")
        ttk.Label(self.root, text=f"配置文件: {config_path}", style="Muted.TLabel").pack(anchor=tk.W, padx=20, pady=(0, 10))

    def _refresh_list(self):
        """刷新热键列表"""
        self.tree.delete(*self.tree.get_children())
        self.item_to_func = {}
        for func_key, func_name in HOTKEY_NAMES.items():
            combo = self.config["hotkeys"].get(func_key, "")
            item_id = self.tree.insert("", tk.END, values=(func_name, combo))
            self.item_to_func[item_id] = func_key

    def _update_status(self):
        """更新状态标签"""
        if self.hotkey_enabled_var.get():
            self.status_label.config(text="● 已启用", style="Success.TLabel")
        else:
            self.status_label.config(text="○ 已禁用", style="Warning.TLabel")

    def _on_toggle_enabled(self):
        """切换热键总开关"""
        self.config["hotkeys_enabled"] = self.hotkey_enabled_var.get()
        save_config(self.config)
        self._update_status()
        log(f"热键总开关: {'启用' if self.hotkey_enabled_var.get() else '禁用'}")

    def _on_double_click(self, event):
        """双击编辑热键"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        func_key = self.item_to_func.get(item)
        if not func_key:
            return
        self._show_capture(item, func_key)

    def _show_capture(self, item_id, func_key):
        """显示热键捕获窗口"""
        capture = tk.Toplevel(self.root)
        capture.title("捕获热键")
        capture.geometry("320x160")
        capture.resizable(False, False)
        capture.transient(self.root)
        capture.grab_set()
        capture.configure(bg=self.bg_card)

        # 居中
        capture.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 320) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 160) // 2
        capture.geometry(f"+{x}+{y}")

        tk.Label(capture, text="请按下新的热键组合", bg=self.bg_card, fg=self.fg,
                 font=("微软雅黑", 11)).pack(pady=(20, 10))
        key_label = tk.Label(capture, text="等待按键...", bg=self.bg_card, fg=self.accent,
                             font=("Consolas", 14, "bold"))
        key_label.pack(pady=5)
        tk.Label(capture, text="按 Esc 取消，按 Delete 清空", bg=self.bg_card, fg=self.fg_muted,
                 font=("微软雅黑", 9)).pack(pady=10)

        captured = {"done": False}

        def on_key_press(event):
            if captured["done"]:
                return
            if event.keysym == "Escape":
                capture.destroy()
                return
            if event.keysym == "Delete":
                # 清空热键
                captured["done"] = True
                key_label.config(text="（已清空）", fg=self.error)
                self.config["hotkeys"][func_key] = ""
                save_config(self.config)
                self.tree.item(item_id, values=(self.tree.item(item_id, "values")[0], ""))
                capture.after(500, capture.destroy)
                return
            # 修饰键不单独触发
            if event.keysym in ("Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R"):
                return
            # 构建组合键
            parts = []
            if event.state & 0x4:
                parts.append("Ctrl")
            if event.state & 0x1:
                parts.append("Shift")
            if event.state & 0x20000:  # Windows Tk Alt位
                parts.append("Alt")
            main_key = event.keysym
            if len(main_key) == 1:
                main_key = main_key.upper()
            parts.append(main_key)
            combo = "+".join(parts)

            captured["done"] = True
            key_label.config(text=combo, fg=self.success)

            # 保存
            self.config["hotkeys"][func_key] = combo
            save_config(self.config)
            self.tree.item(item_id, values=(self.tree.item(item_id, "values")[0], combo))
            log(f"热键已设置: {HOTKEY_NAMES.get(func_key, func_key)} = {combo}")
            capture.after(500, capture.destroy)

        capture.bind("<KeyPress>", on_key_press)
        capture.focus_set()

    def _reset_defaults(self):
        """恢复默认热键"""
        if not messagebox.askyesno("确认", "确定要恢复所有热键为默认值吗？"):
            return
        self.config["hotkeys"] = DEFAULT_HOTKEYS.copy()
        save_config(self.config)
        self._refresh_list()
        log("热键已恢复为默认值")

    def _clear_all(self):
        """清空所有热键"""
        if not messagebox.askyesno("确认", "确定要清空所有热键吗？"):
            return
        for key in self.config["hotkeys"]:
            self.config["hotkeys"][key] = ""
        save_config(self.config)
        self._refresh_list()
        log("所有热键已清空")

    def _save_and_close(self):
        """保存并关闭"""
        save_config(self.config)
        self.root.destroy()

    def run(self):
        """运行"""
        self.root.mainloop()


if __name__ == "__main__":
    init_log()
    app = HotkeyConfigurator()
    app.run()
