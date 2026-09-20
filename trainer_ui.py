# -*- coding: utf-8 -*-
"""
平野孤鸿修改器 - PyQt5 微信三栏布局版
仅界面布局，无业务逻辑

三栏结构：
┌────────┬──────────────┬──────────────────────────┐
│ 左侧导航 │  中间功能列表  │       右侧操作面板        │
│ 70px   │   260px      │      剩余全部宽度          │
│ 深色    │   白色        │                          │
└────────┴──────────────┴──────────────────────────┘

运行：python trainer_ui.py
打包：pyinstaller --onefile --windowed --name TrainerUI trainer_ui.py
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QScrollArea, QTextEdit, QFrame, QSizePolicy, QSpacerItem,
    QLineEdit, QCheckBox, QComboBox, QSlider, QGroupBox, QGridLayout,
    QProgressBar, QTabWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QBrush


# ============================================================
# QSS 样式表（微信风格 + 修改器适配）
# ============================================================
QSS_STYLE = """
/* ===== 全局 ===== */
QWidget {
    font-family: "Microsoft YaHei", "微软雅黑", sans-serif;
    font-size: 13px;
    color: #000000;
}

/* ===== 左侧导航面板 ===== */
#navPanel {
    background-color: #f7f7f7;
    min-width: 70px;
    max-width: 70px;
    border-right: 1px solid #e6e6e6;
}

#navPanel QPushButton {
    background-color: transparent;
    border: none;
    color: #000000;
    font-size: 22px;
    min-height: 55px;
    max-height: 55px;
    border-radius: 6px;
    margin: 2px 8px;
}

#navPanel QPushButton:hover {
    background-color: #e8e8e8;
}

#navPanel QPushButton:checked {
    background-color: #07C160;
    color: #ffffff;
}

#navPanel QLabel {
    background: transparent;
    color: #999999;
    font-size: 10px;
}

/* ===== 中间功能列表面板 ===== */
#funcPanel {
    background-color: #ffffff;
    min-width: 240px;
    border-right: 1px solid #e6e6e6;
}

#funcPanel QListWidget {
    background-color: #ffffff;
    border: none;
    outline: none;
}

#funcPanel QListWidget::item {
    height: 50px;
    background-color: #ffffff;
    border-bottom: 1px solid #f5f5f5;
    padding-left: 8px;
}

#funcPanel QListWidget::item:hover {
    background-color: #f2f2f2;
}

#funcPanel QListWidget::item:selected {
    background-color: #e8f5e9;
    color: #07C160;
}

/* ===== 右侧操作面板 ===== */
#actionPanel {
    background-color: #f5f5f5;
}

#panelTitle {
    background-color: #ffffff;
    border-bottom: 1px solid #e6e6e6;
    min-height: 56px;
    max-height: 56px;
}

#panelTitle QLabel#titleText {
    font-size: 16px;
    font-weight: bold;
    color: #000000;
    background: transparent;
}

#panelTitle QLabel#titleStatus {
    font-size: 12px;
    color: #999999;
    background: transparent;
}

/* ===== 功能卡片 ===== */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e6e6e6;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #000000;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}

/* ===== 按钮样式 ===== */
QPushButton#primaryBtn {
    background-color: #07C160;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton#primaryBtn:hover {
    background-color: #06ad56;
}

QPushButton#primaryBtn:pressed {
    background-color: #05994a;
}

QPushButton#primaryBtn:disabled {
    background-color: #cccccc;
    color: #ffffff;
}

QPushButton#normalBtn {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 7px 16px;
    font-size: 13px;
}

QPushButton#normalBtn:hover {
    border-color: #07C160;
    color: #07C160;
}

QPushButton#dangerBtn {
    background-color: #fa5151;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton#dangerBtn:hover {
    background-color: #e04646;
}

/* ===== 输入框 ===== */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    color: #000000;
    min-height: 20px;
}

QLineEdit:focus {
    border-color: #07C160;
}

QLineEdit:disabled {
    background-color: #f5f5f5;
    color: #999999;
}

/* ===== 复选框 ===== */
QCheckBox {
    spacing: 8px;
    color: #000000;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #d9d9d9;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #07C160;
    border-color: #07C160;
    image: none;
}

/* ===== 下拉框 ===== */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    color: #000000;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #07C160;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #e6e6e6;
    selection-background-color: #e8f5e9;
    selection-color: #07C160;
}

/* ===== 滑块 ===== */
QSlider::groove:horizontal {
    height: 4px;
    background: #e6e6e6;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #07C160;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 16px;
    height: 16px;
    background: #ffffff;
    border: 2px solid #07C160;
    border-radius: 8px;
    margin: -6px 0;
}

/* ===== 日志区 ===== */
#logPanel {
    background-color: #ffffff;
    border-top: 1px solid #e6e6e6;
}

#logPanel QTextEdit {
    background-color: #fafafa;
    border: none;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    color: #333333;
    padding: 8px;
}

/* ===== 状态指示灯 ===== */
QLabel#statusDot {
    font-size: 14px;
    background: transparent;
}

/* ===== 滚动条 ===== */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #cccccc;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #999999;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
"""


# ============================================================
# 功能列表项 Widget
# ============================================================
class FuncItemWidget(QWidget):
    """功能列表项：图标 + 名称 + 描述 + 状态红点"""

    def __init__(self, icon, name, desc, has_dot=False, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        # 图标
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px; background: transparent;")
        icon_label.setFixedWidth(28)
        layout.addWidget(icon_label)

        # 名称 + 描述
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #000000; background: transparent;")
        text_layout.addWidget(name_label)

        desc_label = QLabel(desc)
        desc_label.setStyleSheet("font-size: 11px; color: #999999; background: transparent;")
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout, stretch=1)

        # 状态红点
        if has_dot:
            dot = QLabel("●")
            dot.setStyleSheet("color: #fa5151; font-size: 10px; background: transparent;")
            layout.addWidget(dot, alignment=Qt.AlignTop)


# ============================================================
# 资源行 Widget（资源修改页用）
# ============================================================
class ResourceRow(QWidget):
    """资源行：名称 + 当前值 + 输入框 + 增加按钮"""

    def __init__(self, icon, name, current_value, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # 图标 + 名称
        name_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        icon_label.setFixedWidth(24)
        name_layout.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 13px; color: #000000; background: transparent;")
        name_label.setFixedWidth(60)
        name_layout.addWidget(name_label)
        layout.addLayout(name_layout)

        # 当前值
        current_label = QLabel(f"当前: {current_value:,}")
        current_label.setStyleSheet("font-size: 12px; color: #07C160; font-weight: bold; background: transparent;")
        current_label.setFixedWidth(120)
        layout.addWidget(current_label)

        # 输入框
        self.input_box = QLineEdit("1000000")
        self.input_box.setFixedWidth(100)
        self.input_box.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.input_box)

        # 增加按钮
        add_btn = QPushButton("+增加")
        add_btn.setObjectName("primaryBtn")
        add_btn.setFixedWidth(80)
        add_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(add_btn)

        layout.addStretch()


# ============================================================
# 主窗口
# ============================================================
class TrainerMainWindow(QMainWindow):
    """修改器主窗口 - 微信三栏布局"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("平野孤鸿 全能修改器 v0.3.4 - PyQt5")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        # 中心 Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== 水平 QSplitter 三栏 =====
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        # 第1栏：左侧导航
        splitter.addWidget(self._create_nav_panel())
        # 第2栏：中间功能列表
        splitter.addWidget(self._create_func_panel())
        # 第3栏：右侧操作面板
        splitter.addWidget(self._create_action_panel())

        # 初始宽度
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 0)
        splitter.setStretchFactor(2, 1)
        splitter.setSizes([70, 260, 870])

        main_layout.addWidget(splitter)

        # 应用 QSS
        self.setStyleSheet(QSS_STYLE)

        # 默认选中第一个导航和第一个功能
        self.nav_buttons[0].setChecked(True)
        self._switch_nav(0)

    # ----------------------------------------------------------
    # 第1栏：左侧导航面板
    # ----------------------------------------------------------
    def _create_nav_panel(self):
        panel = QWidget()
        panel.setObjectName("navPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(2)

        # 导航按钮：(图标, 提示, 功能分类)
        nav_items = [
            ("🏠", "主页", "home"),
            ("🎮", "进程", "process"),
            ("⚡", "资源", "resource"),
            ("✨", "创造", "creative"),
            ("🔧", "工具", "tools"),
            ("💾", "存档", "save"),
        ]

        self.nav_buttons = []
        for i, (icon, tooltip, key) in enumerate(nav_items):
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self._switch_nav(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # 底部弹簧 + 设置
        layout.addStretch()

        # Logo
        logo = QLabel("🌿")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(logo)

        settings_btn = QPushButton("⚙️")
        settings_btn.setToolTip("设置")
        settings_btn.setCheckable(True)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(lambda: self._switch_nav(6))
        layout.addWidget(settings_btn)
        self.nav_buttons.append(settings_btn)

        return panel

    # ----------------------------------------------------------
    # 第2栏：中间功能列表面板
    # ----------------------------------------------------------
    def _create_func_panel(self):
        panel = QWidget()
        panel.setObjectName("funcPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 搜索框
        search_container = QWidget()
        search_container.setStyleSheet("background-color: #f7f7f7; padding: 10px;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 8, 10, 8)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 搜索功能...")
        self.search_box.setStyleSheet("""
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
            color: #999999;
        """)
        search_layout.addWidget(self.search_box)
        layout.addWidget(search_container)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e6e6e6; max-height: 1px;")
        layout.addWidget(line)

        # 功能列表
        self.func_list = QListWidget()
        self.func_list.currentRowChanged.connect(self._switch_func)
        layout.addWidget(self.func_list, stretch=1)

        # 各分类的功能列表数据
        self.func_data = {
            0: [  # 主页
                ("📊", "游戏概览", "查看游戏运行状态", False),
                ("🚀", "快速操作", "启动游戏/注入DLL", True),
                ("📈", "状态监控", "实时监控游戏数据", False),
            ],
            1: [  # 进程
                ("🔍", "进程检测", "检测游戏进程", False),
                ("🚀", "启动游戏", "通过Steam启动", False),
                ("🔌", "DLL注入", "注入修改器DLL", True),
                ("📋", "进程信息", "查看进程详细信息", False),
            ],
            2: [  # 资源
                ("💰", "金钱修改", "增加/设置金钱", False),
                ("⛏️", "矿产修改", "增加/设置矿产", False),
                ("🪵", "木料修改", "增加/设置木料", False),
                ("👕", "衣物修改", "增加/设置衣物", False),
                ("🍞", "食物修改", "增加/设置食物", False),
                ("💧", "水源修改", "增加/设置水", False),
                ("🧂", "盐修改", "增加/设置盐", False),
                ("🍷", "酒修改", "增加/设置酒", False),
                ("😊", "幸福度", "设置幸福度", False),
                ("⭐", "知名度", "设置知名度", False),
                ("📦", "一键全资源", "所有资源+100万", False),
            ],
            3: [  # 创造模式
                ("🏆", "鸿业满级", "鸿业等级设为满级", False),
                ("🏗️", "全建筑解锁", "解锁所有建筑", False),
                ("♾️", "无限资源", "建造不消耗资源", False),
                ("⬆️", "无限制升级", "建筑升级无限制", False),
                ("🎯", "全选/反选", "快速选择所有选项", False),
            ],
            4: [  # 高级工具
                ("⏰", "时间控制", "加速/暂停/设置时间", False),
                ("🌤️", "天气控制", "设置天气/季节", False),
                ("👤", "NPC管理", "谋士/居民管理", False),
                ("🏠", "建造控制", "直接建造/销毁建筑", False),
                ("🌍", "SimWorld", "世界系统操作", False),
                ("🏙️", "城市品阶", "品阶逐级提升", False),
                ("🎖️", "Steam成就", "解锁所有成就", False),
                ("🌾", "全地块解锁", "解锁所有地块", False),
            ],
            5: [  # 存档
                ("📂", "存档列表", "查看所有存档", False),
                ("💾", "存档备份", "备份当前存档", False),
                ("♻️", "存档恢复", "恢复备份存档", False),
                ("✏️", "存档编辑", "编辑存档内容", False),
                ("🧹", "清理备份", "清理旧备份文件", False),
            ],
            6: [  # 设置
                ("🎨", "主题设置", "深色/浅色主题", False),
                ("⌨️", "热键设置", "全局热键配置", False),
                ("📝", "日志管理", "日志路径/清空", False),
                ("📦", "MOD管理", "散文件MOD安装/卸载", False),
                ("ℹ️", "关于", "版本信息", False),
            ],
        }

        return panel

    def _switch_nav(self, index):
        """切换左侧导航，更新中间功能列表"""
        # 更新导航按钮选中态
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # 清空功能列表
        self.func_list.clear()

        # 加载对应分类的功能
        items = self.func_data.get(index, [])
        for icon, name, desc, has_dot in items:
            item_widget = FuncItemWidget(icon, name, desc, has_dot)
            list_item = QListWidgetItem(self.func_list)
            list_item.setSizeHint(QSize(0, 50))
            self.func_list.addItem(list_item)
            self.func_list.setItemWidget(list_item, item_widget)

        # 默认选中第一个
        if self.func_list.count() > 0:
            self.func_list.setCurrentRow(0)

    def _switch_func(self, index):
        """切换中间功能项，更新右侧操作面板"""
        if index < 0:
            return
        # 获取当前导航分类
        current_nav = 0
        for i, btn in enumerate(self.nav_buttons):
            if btn.isChecked():
                current_nav = i
                break

        items = self.func_data.get(current_nav, [])
        if index < len(items):
            icon, name, desc, _ = items[index]
            self.title_label.setText(f"{icon} {name}")
            self.title_desc.setText(desc)
            # TODO: 根据功能项切换右侧具体操作界面
            self._update_action_panel(current_nav, index, name)

    # ----------------------------------------------------------
    # 第3栏：右侧操作面板
    # ----------------------------------------------------------
    def _create_action_panel(self):
        panel = QWidget()
        panel.setObjectName("actionPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 顶部标题栏 =====
        title_bar = QWidget()
        title_bar.setObjectName("panelTitle")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(24, 0, 24, 0)

        self.title_label = QLabel("🏠 游戏概览")
        self.title_label.setObjectName("titleText")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        # 状态指示灯
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDot")
        self.status_dot.setStyleSheet("color: #fa5151; background: transparent; font-size: 14px;")
        title_layout.addWidget(self.status_dot)

        self.title_desc = QLabel("未检测到游戏")
        self.title_desc.setObjectName("titleStatus")
        title_layout.addWidget(self.title_desc)

        # 主题切换按钮
        theme_btn = QPushButton("🌙")
        theme_btn.setObjectName("normalBtn")
        theme_btn.setFixedSize(36, 30)
        theme_btn.setCursor(Qt.PointingHandCursor)
        title_layout.addWidget(theme_btn)

        layout.addWidget(title_bar)

        # ===== 中间操作内容区（QScrollArea）=====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        self.action_content = QWidget()
        self.action_layout = QVBoxLayout(self.action_content)
        self.action_layout.setContentsMargins(20, 16, 20, 16)
        self.action_layout.setSpacing(0)
        self.action_layout.addStretch()

        scroll_area.setWidget(self.action_content)
        layout.addWidget(scroll_area, stretch=1)

        # ===== 底部日志区 =====
        log_panel = QWidget()
        log_panel.setObjectName("logPanel")
        log_layout = QVBoxLayout(log_panel)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(0)

        # 日志标题栏
        log_header = QHBoxLayout()
        log_header.setContentsMargins(16, 8, 16, 8)
        log_title = QLabel("📋 操作日志")
        log_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000; background: transparent;")
        log_header.addWidget(log_title)
        log_header.addStretch()

        clear_log_btn = QPushButton("清空")
        clear_log_btn.setObjectName("normalBtn")
        clear_log_btn.setFixedHeight(24)
        clear_log_btn.setCursor(Qt.PointingHandCursor)
        log_header.addWidget(clear_log_btn)

        log_layout.addLayout(log_header)

        # 日志内容
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setPlainText("[INFO] 修改器已启动\n[INFO] 等待游戏进程...\n")
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_panel)

        return panel

    def _update_action_panel(self, nav_index, func_index, func_name):
        """根据选中的功能项更新右侧操作面板（仅布局示例，无业务逻辑）"""
        # 清空现有内容
        while self.action_layout.count() > 0:
            item = self.action_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 根据功能类型显示不同的操作界面
        if nav_index == 2:  # 资源修改
            self._build_resource_panel(func_name)
        elif nav_index == 3:  # 创造模式
            self._build_creative_panel()
        elif nav_index == 0:  # 主页
            self._build_home_panel()
        elif nav_index == 1:  # 进程
            self._build_process_panel()
        else:
            self._build_placeholder(func_name)

        self.action_layout.addStretch()

    def _build_home_panel(self):
        """主页：概览卡片 + 快速操作"""
        # 状态卡片行
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        cards = [
            ("游戏状态", "未运行", "#fa5151"),
            ("DLL状态", "未注入", "#fa9d3b"),
            ("Lua通道", "未连接", "#999999"),
        ]
        for title, value, color in cards:
            card = QGroupBox()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)
            t = QLabel(title)
            t.setStyleSheet("font-size: 12px; color: #999999; background: transparent;")
            card_layout.addWidget(t)
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; background: transparent;")
            card_layout.addWidget(v)
            cards_layout.addWidget(card)

        self.action_layout.addLayout(cards_layout)

        # 快速操作
        quick_group = QGroupBox("🚀 快速操作")
        quick_layout = QHBoxLayout(quick_group)
        quick_layout.setContentsMargins(16, 16, 16, 16)
        quick_layout.setSpacing(10)

        launch_btn = QPushButton("启动游戏")
        launch_btn.setObjectName("primaryBtn")
        launch_btn.setCursor(Qt.PointingHandCursor)
        quick_layout.addWidget(launch_btn)

        inject_btn = QPushButton("注入DLL")
        inject_btn.setObjectName("primaryBtn")
        inject_btn.setCursor(Qt.PointingHandCursor)
        quick_layout.addWidget(inject_btn)

        detect_btn = QPushButton("检测进程")
        detect_btn.setObjectName("normalBtn")
        detect_btn.setCursor(Qt.PointingHandCursor)
        quick_layout.addWidget(detect_btn)

        quick_layout.addStretch()
        self.action_layout.addWidget(quick_group)

    def _build_process_panel(self):
        """进程页"""
        group = QGroupBox("🎮 进程操作")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        for text in ["检测游戏进程", "启动游戏", "注入DLL"]:
            btn = QPushButton(text)
            btn.setObjectName("primaryBtn" if "启动" in text or "注入" in text else "normalBtn")
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
        layout.addStretch()
        self.action_layout.addWidget(group)

        info_group = QGroupBox("📋 进程信息")
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_label = QLabel("未检测到游戏进程\n\n请先启动游戏，然后点击「检测游戏进程」")
        info_label.setStyleSheet("color: #999999; font-size: 13px; background: transparent;")
        info_layout.addWidget(info_label)
        self.action_layout.addWidget(info_group)

    def _build_resource_panel(self, func_name):
        """资源修改页：资源行列表"""
        # 快捷操作
        quick_group = QGroupBox("⚡ 快捷操作")
        quick_layout = QHBoxLayout(quick_group)
        quick_layout.setContentsMargins(16, 12, 16, 12)
        quick_layout.setSpacing(10)

        all_btn = QPushButton("📦 一键全部资源 +100万")
        all_btn.setObjectName("primaryBtn")
        all_btn.setCursor(Qt.PointingHandCursor)
        quick_layout.addWidget(all_btn)

        zero_btn = QPushButton("🗑️ 资源归零")
        zero_btn.setObjectName("dangerBtn")
        zero_btn.setCursor(Qt.PointingHandCursor)
        quick_layout.addWidget(zero_btn)
        quick_layout.addStretch()
        self.action_layout.addWidget(quick_group)

        # 资源列表
        res_group = QGroupBox("💰 资源修改")
        res_layout = QVBoxLayout(res_group)
        res_layout.setContentsMargins(8, 12, 8, 12)
        res_layout.setSpacing(2)

        resources = [
            ("💰", "金钱", 3513844),
            ("⛏️", "矿产", 1250000),
            ("🪵", "木料", 980000),
            ("👕", "衣物", 450000),
            ("🍞", "食物", 2100000),
            ("💧", "水", 1800000),
            ("🧂", "盐", 320000),
            ("🍷", "酒", 150000),
        ]
        for icon, name, value in resources:
            row = ResourceRow(icon, name, value)
            res_layout.addWidget(row)

        self.action_layout.addWidget(res_group)

        # 特殊属性
        special_group = QGroupBox("✨ 特殊属性")
        special_layout = QHBoxLayout(special_group)
        special_layout.setContentsMargins(16, 12, 16, 12)
        special_layout.setSpacing(10)

        happy_btn = QPushButton("😊 幸福度 +100")
        happy_btn.setObjectName("normalBtn")
        happy_btn.setCursor(Qt.PointingHandCursor)
        special_layout.addWidget(happy_btn)

        fame_btn = QPushButton("⭐ 知名度 +10000")
        fame_btn.setObjectName("normalBtn")
        fame_btn.setCursor(Qt.PointingHandCursor)
        special_layout.addWidget(fame_btn)
        special_layout.addStretch()
        self.action_layout.addWidget(special_group)

    def _build_creative_panel(self):
        """创造模式页：复选框 + 按钮"""
        group = QGroupBox("✨ 创造模式选项")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        options = [
            ("🏆 鸿业满级", "鸿业等级设为14级（满级）"),
            ("🏗️ 全建筑解锁", "解锁所有建筑类型"),
            ("♾️ 无限资源", "建造/升级不消耗资源"),
            ("⬆️ 无限制升级", "建筑升级无等级限制"),
        ]
        for text, desc in options:
            checkbox = QCheckBox(f"{text}  -  {desc}")
            checkbox.setCursor(Qt.PointingHandCursor)
            layout.addWidget(checkbox)

        # 全选/反选
        select_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        select_all_btn.setObjectName("normalBtn")
        select_all_btn.setCursor(Qt.PointingHandCursor)
        select_layout.addWidget(select_all_btn)

        invert_btn = QPushButton("反选")
        invert_btn.setObjectName("normalBtn")
        invert_btn.setCursor(Qt.PointingHandCursor)
        select_layout.addWidget(invert_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)

        self.action_layout.addWidget(group)

        # 操作按钮
        action_layout = QHBoxLayout()
        enable_btn = QPushButton("开启创造模式")
        enable_btn.setObjectName("primaryBtn")
        enable_btn.setCursor(Qt.PointingHandCursor)
        action_layout.addWidget(enable_btn)

        disable_btn = QPushButton("关闭创造模式")
        disable_btn.setObjectName("dangerBtn")
        disable_btn.setCursor(Qt.PointingHandCursor)
        action_layout.addWidget(disable_btn)
        action_layout.addStretch()
        self.action_layout.addLayout(action_layout)

    def _build_placeholder(self, func_name):
        """占位页面"""
        group = QGroupBox(f"🔧 {func_name}")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 20)

        label = QLabel(f"「{func_name}」功能界面开发中...\n\n此处将放置对应的操作控件：数值输入框、开关、滑块、按钮等")
        label.setStyleSheet("color: #999999; font-size: 13px; background: transparent;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.action_layout.addWidget(group)


# ============================================================
# 程序入口
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = TrainerMainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


# ============================================================
# PyInstaller 打包命令：
# ============================================================
# 基础打包：
#   pyinstaller --onefile --windowed --name PingYeTrainer trainer_ui.py
#
# 带图标：
#   pyinstaller --onefile --windowed --icon=app.ico --name PingYeTrainer trainer_ui.py
#
# 打包到 dist 目录：
#   pyinstaller --onefile --windowed --distpath ./dist --name PingYeTrainer trainer_ui.py
#
# 注意：打包前需安装 pyinstaller: pip install pyinstaller
# ============================================================
