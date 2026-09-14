"""
顶部 KPI 数据条（融合版 UI）

常驻显示核心实时数据，玩家切回修改器即可一眼读完游戏状态，无需滚动页面。
数据来源：GameStatusProvider 单例（与其他页面共享同一份缓存，不新增轮询）。
"""
import tkinter as tk
from tkinter import ttk

from src.game_status import get_status_provider
from src.logger import log_warning
from .theme import FONT_MONO_BOLD, FONT_TINY
from .widgets import T
from .rounded import RoundedFrame

# (status 字段, 中文标签, 格式化, 颜色键)
KPI_DEFS = [
    ("money", "金钱", "num", "warning"),
    ("population", "人口", "num", "fg"),
    ("pop_max", "人口上限", "num", "fg_muted"),
    ("wood", "木料", "num", "fg"),
    ("mineral", "矿产", "num", "fg"),
    ("day_stamp", "游戏天数", "day", "fg"),
    ("speed_mult", "倍速", "mult", "accent"),
]

_ROWS = (KPI_DEFS[:4], KPI_DEFS[4:])


def _fmt(val, kind):
    """按类型格式化数值；None → '--'"""
    if val is None:
        return "--"
    try:
        f = float(val)
    except (TypeError, ValueError):
        return str(val)
    if kind == "day":
        return "%d 日" % int(f)
    if kind == "mult":
        return "%.2fx" % f
    if abs(f) >= 10000:
        return "{:,}".format(int(round(f)))
    if f == int(f):
        return "%d" % int(f)
    return "%.1f" % f


class KpiBar(ttk.Frame):
    """顶部 KPI 数据条（4 + 3 紧凑卡片，弱边框、标签弱化、数值高亮）。"""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._cards = {}
        for row in _ROWS:
            row_frame = ttk.Frame(self, style="TFrame")
            row_frame.pack(fill=tk.X, pady=(0, 4))
            for i, (key, label, kind, color_key) in enumerate(row):
                card = RoundedFrame(row_frame, radius=8, fill_key="bg_card",
                                    outline_key="bg_elevated")
                card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0 if i == 0 else 6, 0))
                tk.Label(card.body, text=label, bg=T("bg_card"), fg=T("fg_muted"),
                         font=FONT_TINY).pack(anchor="w", padx=8, pady=(4, 0))
                v = tk.Label(card.body, text="--", bg=T("bg_card"), fg=T(color_key),
                             font=FONT_MONO_BOLD)
                v.pack(anchor="w", padx=8, pady=(0, 4))
                self._cards[key] = (v, kind, color_key)

        self._provider = get_status_provider()
        self._provider.subscribe("kpi_bar", self._on_status)
        self.bind("<Destroy>", self._on_destroy)

    def _on_status(self, status, success):
        """Provider 回调（在工作线程）：转到主线程更新控件"""
        try:
            self.after(0, self._apply, status or {}, success)
        except Exception:
            pass

    def _apply(self, status, success):
        for key, (lbl, kind, color_key) in self._cards.items():
            val = status.get(key)
            try:
                lbl.configure(text=_fmt(val, kind) if success else "--")
            except tk.TclError:
                return
            # 动态着色：人口接近上限 → 黄；金钱/木料/矿产 为 0 → 红
            color = T(color_key)
            try:
                if success and val is not None:
                    f = float(val)
                    if key == "population":
                        pm = float(status.get("pop_max") or 0)
                        if pm > 0 and f / pm >= 0.85:
                            color = T("warning")
                    elif key in ("money", "wood", "mineral") and f <= 0:
                        color = T("error")
            except (TypeError, ValueError):
                pass
            try:
                lbl.configure(fg=color)
            except tk.TclError:
                return

    def _on_destroy(self, event=None):
        if event is not None and event.widget is not self:
            return
        try:
            self._provider.unsubscribe("kpi_bar")
        except Exception as e:
            log_warning(f"KPI 条退订失败: {e}")
