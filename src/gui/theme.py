"""
主题管理模块
功能：三套主题一键切换，支持动态切换所有UI组件颜色

主题设计（v0.3 融合版）：
    - shenjian（深简）：方案A 瑞士极简 · 深色 + 绿强调（默认，悬浮游戏窗口低干扰）
    - bento（Bento）：方案B 数据密集 · 更深的暗底 + 卡片色块（高频监控）
    - mojian（墨笺）：方案C E-Ink 优化 · 米纸底 + 朱红强调（贴合《平野鸿孤》国风）

设计原则：**布局代码只有一套，主题仅切换色板 / 少量字体质感**。

使用方式：
    from src.gui.theme import ThemeManager, get_theme
    ThemeManager.apply(style, root, "shenjian")
    ThemeManager.apply(style, root)      # 循环切到下一个主题
"""
import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------- 字体（唯一定义源）
# GUI 各处的 font=(...) 一律引用这里的常量，避免重复的字体元组散落各处
FONT_TITLE = ("微软雅黑", 14, "bold")
FONT_SUB = ("微软雅黑", 11, "bold")
FONT_BOLD = ("微软雅黑", 10, "bold")
FONT_BODY = ("微软雅黑", 10)
FONT_TINY = ("微软雅黑", 9)
FONT_MONO_LG = ("Consolas", 12, "bold")
FONT_MONO_BOLD = ("Consolas", 10, "bold")
FONT_MONO = ("Consolas", 9)


# ---------------------------------------------------------------- 三套色板
# 主题 1：深简（方案A · 瑞士极简）
SHENJIAN = {
    "name": "shenjian",
    "label": "深简",
    # 背景层级（由深到浅）
    "bg":           "#0F172A",   # 主背景
    "bg_surface":   "#0B1220",   # 最深（日志区）
    "bg_card":      "#1B2336",   # 卡片/面板
    "bg_elevated":  "#222C44",   # 按钮悬浮
    "bg_selected":  "#2A3650",   # 选中态
    # 文字
    "fg":           "#F8FAFC",   # 主文字
    "fg_muted":     "#94A3B8",   # 次要文字
    "fg_bright":    "#E2E8F0",   # 高亮文字
    # 强调色
    "accent":       "#22C55E",   # 主强调（绿）
    "accent_hover": "#16A34A",   # 悬浮态
    # 语义色
    "success":      "#22C55E",
    "warning":      "#F59E0B",
    "error":        "#EF4444",
    "info":         "#3B82F6",
}

# 主题 2：Bento（方案B · 数据密集）
BENTO = {
    "name": "bento",
    "label": "Bento",
    "bg":           "#020617",   # 更深的暗底
    "bg_surface":   "#01040F",
    "bg_card":      "#0E1223",
    "bg_elevated":  "#1A1E2F",
    "bg_selected":  "#262C40",
    "fg":           "#F8FAFC",
    "fg_muted":     "#94A3B8",
    "fg_bright":    "#E2E8F0",
    "accent":       "#22C55E",
    "accent_hover": "#16A34A",
    "success":      "#22C55E",
    "warning":      "#F59E0B",
    "error":        "#EF4444",
    "info":         "#3B82F6",
}

# 主题 3：墨笺（方案C · E-Ink 米纸，降低刺眼）
MOJIAN = {
    "name": "mojian",
    "label": "墨笺",
    "bg":           "#F3EDE1",   # 米纸底（非纯白，避免刺眼）
    "bg_surface":   "#EAE2D2",   # 日志区
    "bg_card":      "#FBF8F1",
    "bg_elevated":  "#EFE7D8",
    "bg_selected":  "#E2D8C4",
    "fg":           "#1E1A15",   # 墨黑
    "fg_muted":     "#5C5449",   # 淡墨（仍 >= 4.5:1）
    "fg_bright":    "#7A1F18",
    "accent":       "#9E2B22",   # 朱红
    "accent_hover": "#7F221B",
    "success":      "#2F6B45",
    "warning":      "#8A6A16",
    "error":        "#B3352A",
    "info":         "#2B5E8A",
}

# 主题映射 + 切换顺序
THEMES = {"shenjian": SHENJIAN, "bento": BENTO, "mojian": MOJIAN}
THEME_ORDER = ["shenjian", "bento", "mojian"]
THEME_LABELS = {"shenjian": "深简", "bento": "Bento", "mojian": "墨笺"}
_current = "shenjian"


def get_theme():
    """获取当前主题字典"""
    return THEMES[_current]


def get_theme_name():
    """获取当前主题名称"""
    return _current


def next_theme():
    """返回循环顺序中的下一个主题名"""
    i = THEME_ORDER.index(_current) if _current in THEME_ORDER else 0
    return THEME_ORDER[(i + 1) % len(THEME_ORDER)]


class ThemeManager:
    """主题管理器：统一应用和管理三套主题"""

    @staticmethod
    def apply(style, root, theme_name=None):
        """应用指定主题（theme_name=None 时循环切到下一个主题）

        参数：
            style: ttk.Style 实例
            root: tk.Tk 根窗口
            theme_name: "shenjian" / "bento" / "mojian"
        """
        global _current
        if theme_name and theme_name in THEMES:
            _current = theme_name
        elif not theme_name:
            _current = next_theme()

        t = THEMES[_current]

        # 根窗口背景
        root.configure(bg=t["bg"])

        # 标签页（选中态强化：更亮背景+加粗文字）
        style.configure("TNotebook", background=t["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=t["bg_card"], foreground=t["fg_muted"],
                        padding=[18, 10], font=FONT_BODY)
        style.map("TNotebook.Tab",
                  background=[("selected", t["bg_elevated"]), ("active", t["bg_selected"])],
                  foreground=[("selected", t["accent"]), ("active", t["fg"])])

        # 框架
        style.configure("TFrame", background=t["bg"])
        style.configure("Card.TFrame", background=t["bg_card"], relief="flat")

        # 标签
        style.configure("TLabel", background=t["bg"], foreground=t["fg"], font=FONT_BODY)
        style.configure("Card.TLabel", background=t["bg_card"], foreground=t["fg"], font=FONT_BODY)
        style.configure("Title.TLabel", background=t["bg"], foreground=t["accent"],
                        font=FONT_TITLE)
        style.configure("Success.TLabel", background=t["bg"], foreground=t["success"], font=FONT_BODY)
        style.configure("Warning.TLabel", background=t["bg"], foreground=t["warning"], font=FONT_BODY)
        style.configure("Error.TLabel", background=t["bg"], foreground=t["error"], font=FONT_BODY)

        # 按钮（统一高度28px，hover亮度提升，active下沉效果）
        style.configure("TButton", background=t["bg_elevated"], foreground=t["fg"],
                        font=FONT_BODY, padding=[14, 7], borderwidth=0)
        style.map("TButton",
                  background=[("active", t["bg_selected"]), ("hover", t["bg_selected"])],
                  foreground=[("active", t["fg_bright"]), ("hover", t["fg_bright"])])

        style.configure("Primary.TButton", background=t["accent"], foreground=t["bg"],
                        font=FONT_BOLD, padding=[16, 8], borderwidth=0)
        style.map("Primary.TButton",
                  background=[("active", t["accent_hover"]), ("hover", t["accent_hover"])])

        style.configure("Success.TButton", background=t["success"], foreground=t["bg"],
                        font=FONT_BOLD, padding=[16, 8], borderwidth=0)
        style.map("Success.TButton",
                  background=[("active", t["success"]), ("hover", t["success"])])

        style.configure("Danger.TButton", background=t["error"], foreground=t["bg"],
                        font=FONT_BOLD, padding=[16, 8], borderwidth=0)
        style.map("Danger.TButton",
                  background=[("active", t["error"]), ("hover", t["error"])])

        style.configure("Small.TButton", background=t["bg_elevated"], foreground=t["fg"],
                        font=FONT_TINY, padding=[8, 3], borderwidth=0)
        style.map("Small.TButton",
                  background=[("active", t["bg_selected"])],
                  foreground=[("active", t["fg_bright"])])

        # 左侧导航按钮（PCL2 风格：左对齐；选中态强调色）
        style.configure("Nav.TButton", background=t["bg_card"], foreground=t["fg_muted"],
                        font=FONT_BODY, padding=[16, 10], anchor="w", borderwidth=0)
        style.map("Nav.TButton",
                  background=[("active", t["bg_elevated"]), ("hover", t["bg_elevated"])],
                  foreground=[("active", t["accent"]), ("hover", t["accent"])])
        style.configure("NavActive.TButton", background=t["bg_elevated"], foreground=t["accent"],
                        font=FONT_BOLD, padding=[16, 10], anchor="w", borderwidth=0)
        style.map("NavActive.TButton",
                  background=[("active", t["bg_selected"]), ("hover", t["bg_selected"])],
                  foreground=[("active", t["accent"]), ("hover", t["accent"])])

        # 恢复按钮样式
        style.configure("Restore.TButton", background=t["warning"], foreground=t["bg"],
                        font=("微软雅黑", 9, "bold"), padding=[8, 3], borderwidth=0)
        style.map("Restore.TButton",
                  background=[("active", t["bg_selected"])])

        # 次要按钮（灰色）
        style.configure("Secondary.TButton", background=t["bg_elevated"], foreground=t["fg_muted"],
                        font=FONT_BODY, padding=[12, 6], borderwidth=0)
        style.map("Secondary.TButton",
                  background=[("active", t["bg_selected"])],
                  foreground=[("active", t["fg"])])

        # 主题切换芯片（顶部三主题切换）
        style.configure("ThemeChip.TButton", background=t["bg_selected"], foreground=t["fg_muted"],
                        font=FONT_TINY, padding=[10, 4], borderwidth=0)
        style.map("ThemeChip.TButton",
                  background=[("active", t["bg_elevated"]), ("hover", t["bg_elevated"])],
                  foreground=[("active", t["fg"]), ("hover", t["fg"])])
        style.configure("ThemeChipActive.TButton", background=t["accent"], foreground=t["bg"],
                        font=FONT_TINY, padding=[10, 4], borderwidth=0)
        style.map("ThemeChipActive.TButton",
                  background=[("active", t["accent_hover"]), ("hover", t["accent_hover"])])

        # KPI 数值标签（顶部数据条）
        style.configure("KpiKey.TLabel", background=t["bg_card"], foreground=t["fg_muted"],
                        font=FONT_TINY)
        style.configure("KpiValue.TLabel", background=t["bg_card"], foreground=t["fg"],
                        font=FONT_MONO_BOLD)

        # 状态指示灯标签（绿点/黄点/红点 + 文字）
        style.configure("Status.TLabel", background=t["bg_card"], foreground=t["fg"],
                        font=FONT_BODY)
        style.configure("StatusSuccess.TLabel", background=t["bg_card"], foreground=t["success"],
                        font=FONT_BOLD)
        style.configure("StatusWarning.TLabel", background=t["bg_card"], foreground=t["warning"],
                        font=FONT_BOLD)
        style.configure("StatusError.TLabel", background=t["bg_card"], foreground=t["error"],
                        font=FONT_BOLD)

        # 禁用状态按钮（置灰）
        style.configure("Disabled.TButton", background=t["bg_card"], foreground=t["fg_muted"],
                        font=FONT_BODY, padding=[12, 6], borderwidth=0)

        # 输入框
        style.configure("TEntry", fieldbackground=t["bg_card"], foreground=t["fg"],
                        insertcolor=t["fg"], borderwidth=0)

        # 组合框
        style.configure("TCombobox", fieldbackground=t["bg_card"], foreground=t["fg"],
                        background=t["bg_elevated"], borderwidth=0)

        # 进度条
        style.configure("Horizontal.TProgressbar", background=t["accent"], troughcolor=t["bg_card"], borderwidth=0)

        # Treeview
        style.configure("Treeview",
                        background=t["bg_card"],
                        foreground=t["fg"],
                        fieldbackground=t["bg_card"],
                        borderwidth=0,
                        rowheight=24,
                        font=FONT_TINY)
        style.configure("Treeview.Heading",
                        background=t["bg_elevated"],
                        foreground=t["fg"],
                        borderwidth=0,
                        font=("微软雅黑", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", t["bg_selected"])],
                  foreground=[("selected", t["fg_bright"])])
        style.map("Treeview.Heading",
                  background=[("active", t["bg_selected"])])

        # 滚动条
        style.configure("TScrollbar",
                        background=t["bg_card"],
                        troughcolor=t["bg"],
                        borderwidth=0,
                        arrowcolor=t["fg"])
        style.map("TScrollbar",
                  background=[("active", t["bg_elevated"])])

    @staticmethod
    def toggle(style, root):
        """按 深简 → Bento → 墨笺 循环切换，返回切换后的主题名"""
        ThemeManager.apply(style, root)
        return _current

    @staticmethod
    def get_color(key):
        """获取当前主题中指定键的颜色值"""
        return THEMES[_current].get(key, "#000000")

    @staticmethod
    def get_log_colors():
        """获取日志区颜色配置（bg, fg, insertbg）"""
        t = THEMES[_current]
        return t["bg_surface"], t["fg"], t["fg"]
