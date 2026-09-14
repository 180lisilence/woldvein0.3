"""
圆角组件（tkinter 原生 Frame / ttk.Button 都是直角，这里用 Canvas 真画圆角）

- RoundedFrame：圆角容器，内容放在 .body（普通 Frame）里
- RoundedButton：圆角按钮，API 尽量对齐 ttk.Button（text/state/style/command/width）
- redraw_all()：主题切换后重绘所有圆角组件（Canvas 不受 ttk 样式影响）

约束：tkinter 无真阴影/毛玻璃；圆角用「Canvas 平滑多边形」实现，视觉近似。
"""
import tkinter as tk
from tkinter import font as tkfont

from .widgets import T

_REGISTRY = []

# 样式名 → (底色键, 文字色键, 悬浮色键, 高度, 左右内边距, 是否加粗)
_STYLE_MAP = {
    "Primary.TButton":          ("accent", "bg", "accent_hover", 28, 14, True),
    "Success.TButton":          ("success", "bg", "success", 28, 14, True),
    "Warning.TButton":          ("warning", "bg", "warning", 28, 14, True),
    "Danger.TButton":           ("error", "bg", "error", 28, 14, True),
    "Restore.TButton":          ("warning", "bg", "bg_selected", 22, 8, True),
    "Small.TButton":            ("bg_elevated", "fg", "bg_selected", 22, 8, False),
    "Secondary.TButton":        ("bg_elevated", "fg_muted", "bg_selected", 28, 12, False),
    "Nav.TButton":              ("bg_card", "fg_muted", "bg_elevated", 34, 14, False),
    "NavActive.TButton":        ("bg_elevated", "accent", "bg_selected", 34, 14, True),
    "ThemeChip.TButton":        ("bg_selected", "fg_muted", "bg_elevated", 22, 10, False),
    "ThemeChipActive.TButton":  ("accent", "bg", "accent_hover", 22, 10, False),
    "Disabled.TButton":         ("bg_card", "fg_muted", "bg_card", 26, 12, False),
}
_DEFAULT_STYLE = ("bg_elevated", "fg", "bg_selected", 28, 14, False)


def _round_rect(canvas, x0, y0, x1, y1, r, **kw):
    """在 Canvas 上画平滑圆角矩形（返回 item id）"""
    pts = [
        x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
        x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
        x0, y1, x0, y1 - r, x0, y0 + r, x0, y0,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


def redraw_all():
    """主题切换后重绘所有圆角组件"""
    alive = []
    for w in _REGISTRY:
        try:
            if w.winfo_exists():
                w.redraw()
                alive.append(w)
        except tk.TclError:
            pass
    _REGISTRY[:] = alive


# ============================================================
# 圆角容器
# ============================================================
class RoundedFrame(tk.Frame):
    """圆角容器；把内容放进 .body 即可。

    实现：外层仍是普通 tk.Frame（尺寸由内容决定，不改变原布局语义），
    圆角背景由一层 place 满铺的 Canvas 绘制并置于最底层。
    参数：
        fill_key / outline_key：取自当前主题的颜色键（见 theme.THEMES）
    """

    def __init__(self, parent, radius=10, fill_key="bg_card",
                 outline_key="bg_elevated", padding=2, **kw):
        super().__init__(parent, bg=T(fill_key), **kw)
        self._radius = radius
        self._fill_key = fill_key
        self._outline_key = outline_key
        self._padding = padding
        self._bg = tk.Canvas(self, highlightthickness=0, bd=0, takefocus=0)
        self._bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.body = tk.Frame(self, bg=T(fill_key))
        self.body.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        self.bind("<Configure>", self._on_configure)
        _REGISTRY.append(self)

    def _on_configure(self, _=None):
        self.redraw()

    def redraw(self):
        try:
            w = self.winfo_width()
            h = self.winfo_height()
        except tk.TclError:
            return
        if w <= 2 or h <= 2:
            return
        fill = T(self._fill_key)
        outline = T(self._outline_key)
        self.configure(bg=fill)
        self.body.configure(bg=fill)
        self._bg.configure(bg=fill)
        self._bg.delete("all")
        _round_rect(self._bg, 1, 1, w - 1, h - 1, self._radius,
                    fill=fill, outline=outline, width=1)
        try:
            self._bg.lower()  # 背景层压到内容之下
        except tk.TclError:
            pass


# ============================================================
# 圆角按钮（API 兼容 ttk.Button 的常用子集）
# ============================================================
class RoundedButton(tk.Canvas):
    """圆角按钮（Canvas 绘制）。支持 text / style / command / state / width。

    兼容方法：configure/config(text/state/style/command/width)、cget("text"/"state")、invoke()
    """

    def __init__(self, parent, text="", command=None, style=None, width=None,
                 state=tk.NORMAL, radius=6, **kw):
        self._style = style or "TButton"
        self._text = text
        self._command = command
        self._state = state
        self._radius = radius
        self._hover = False
        self._size = self._measure(text, width)
        super().__init__(parent, width=self._size[0], height=self._size[1],
                         highlightthickness=0, bd=0, takefocus=0, cursor="hand2")
        self._fill = None
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        _REGISTRY.append(self)
        self.redraw()

    # ---- 内部 ----
    def _style_tuple(self):
        return _STYLE_MAP.get(self._style, _DEFAULT_STYLE)

    def _measure(self, text, width_chars=None):
        _, _, _, h, padx, bold = self._style_tuple()
        f = tkfont.Font(font=("微软雅黑", 10, "bold") if bold else ("微软雅黑", 10))
        tw = f.measure(str(text or ""))
        if width_chars:
            tw = max(tw, f.measure("0") * int(width_chars))
        return (tw + 2 * padx, h)

    def redraw(self):
        try:
            w, h = self._size
            bgk, fgk, hoverk, _, _, _ = self._style_tuple()
            disabled = str(self._state) == "disabled"
            if disabled:
                fill_key, fg_key = "bg_card", "fg_muted"
            elif self._hover:
                fill_key, fg_key = hoverk, fgk
                if fill_key.endswith("_hover"):
                    fg_key = "bg"
            else:
                fill_key, fg_key = bgk, fgk
            fill, fg = T(fill_key), T(fg_key)
            self.configure(bg=self._parent_bg())
            self.delete("all")
            _round_rect(self, 1, 1, w - 1, h - 1, self._radius,
                        fill=fill, outline=fill, width=1)
            self.create_text(w // 2, h // 2, text=str(self._text or ""), fill=fg,
                             font=("微软雅黑", 10, "bold") if self._style_tuple()[5] else ("微软雅黑", 10))
            self._fill = fill
        except tk.TclError:
            pass

    def _parent_bg(self):
        """推断父容器底色，避免圆角四角出现杂色"""
        m = self.master
        try:
            if "bg" in m.keys():
                return m.cget("bg")
        except Exception:
            pass
        try:
            st = str(m.cget("style"))
            return T("bg_card") if "Card" in st else T("bg")
        except Exception:
            return T("bg")

    def _on_enter(self, _=None):
        self._hover = True
        self.redraw()

    def _on_leave(self, _=None):
        self._hover = False
        self.redraw()

    def _on_press(self, _=None):
        if str(self._state) == "disabled":
            return
        self.move("all", 0, 1)

    def _on_release(self, _=None):
        if str(self._state) == "disabled":
            return
        self.redraw()
        if callable(self._command):
            self._command()

    def invoke(self):
        if str(self._state) != "disabled" and callable(self._command):
            self._command()

    # ---- 兼容 ttk.Button 的接口 ----
    def configure(self, cnf=None, **kw):
        cnf = dict(cnf or {})
        cnf.update(kw)
        need = False
        if "text" in cnf:
            self._text = cnf.pop("text")
            need = True
        if "state" in cnf:
            self._state = cnf.pop("state")
            need = True
        if "command" in cnf:
            self._command = cnf.pop("command")
        if "style" in cnf:
            self._style = cnf.pop("style")
            need = True
        wcs = cnf.pop("width", None)
        if wcs is not None:
            need = True
        if cnf:
            try:
                tk.Canvas.configure(self, **cnf)
            except tk.TclError:
                pass
        if need:
            self._size = self._measure(self._text, wcs)
            try:
                tk.Canvas.configure(self, width=self._size[0], height=self._size[1])
            except tk.TclError:
                pass
            self.redraw()

    config = configure

    def cget(self, key):
        if key == "text":
            return self._text
        if key == "state":
            return self._state
        if key == "style":
            return self._style
        return tk.Canvas.cget(self, key)
