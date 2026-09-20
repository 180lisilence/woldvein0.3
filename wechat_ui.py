# -*- coding: utf-8 -*-
"""
微信电脑客户端三栏UI布局 - PyQt5 复刻版
仅界面布局，无业务逻辑

布局结构（水平 QSplitter 三栏）：
┌────────┬──────────────┬──────────────────────────┐
│ 左侧导航 │  中间会话列表  │       右侧聊天面板        │
│ 70px   │   260px      │      剩余全部宽度          │
│ 深色    │   白色        │                          │
└────────┴──────────────┴──────────────────────────┘

运行：python wechat_ui.py
打包：pyinstaller --onefile --windowed --name WeChatUI wechat_ui.py
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QScrollArea, QTextEdit, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QBrush


# ============================================================
# QSS 样式表（微信风格）
# ============================================================
QSS_STYLE = """
/* ===== 全局 ===== */
QWidget {
    font-family: "Microsoft YaHei", "微软雅黑", sans-serif;
    font-size: 13px;
    color: #333333;
}

/* ===== 左侧导航面板 ===== */
#navPanel {
    background-color: #262626;
    min-width: 70px;
    max-width: 70px;
}

#navPanel QPushButton {
    background-color: transparent;
    border: none;
    color: #999999;
    font-size: 22px;
    min-height: 50px;
    max-height: 50px;
    border-radius: 4px;
}

#navPanel QPushButton:hover {
    background-color: #383838;
    color: #ffffff;
}

#navPanel QPushButton:checked {
    background-color: #383838;
    color: #07C160;
}

/* ===== 中间会话列表面板 ===== */
#sessionPanel {
    background-color: #ffffff;
    min-width: 260px;
}

#sessionPanel QListWidget {
    background-color: #ffffff;
    border: none;
    outline: none;
}

#sessionPanel QListWidget::item {
    height: 65px;
    background-color: #ffffff;
    border-bottom: 1px solid #f0f0f0;
}

#sessionPanel QListWidget::item:hover {
    background-color: #f2f2f2;
}

#sessionPanel QListWidget::item:selected {
    background-color: #e8f5e9;
    color: #333333;
}

/* ===== 右侧聊天面板 ===== */
#chatPanel {
    background-color: #f5f5f5;
}

#chatTitle {
    background-color: #f5f5f5;
    border-bottom: 1px solid #e6e6e6;
    min-height: 50px;
    max-height: 50px;
}

#chatTitle QLabel {
    background-color: transparent;
    font-size: 15px;
    font-weight: bold;
    color: #333333;
}

#chatContent {
    background-color: #f5f5f5;
    border: none;
}

#chatInput {
    background-color: #ffffff;
    border-top: 1px solid #e6e6e6;
    min-height: 120px;
}

#chatInput QTextEdit {
    background-color: #ffffff;
    border: none;
    font-size: 13px;
    color: #333333;
    padding: 8px;
}

#sendBtn {
    background-color: #07C160;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 6px 20px;
    font-size: 13px;
    min-width: 70px;
}

#sendBtn:hover {
    background-color: #06ad56;
}

#sendBtn:pressed {
    background-color: #05994a;
}

#emojiBtn {
    background-color: transparent;
    border: none;
    font-size: 18px;
    color: #666666;
    min-width: 36px;
    max-width: 36px;
}

#emojiBtn:hover {
    color: #07C160;
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
# 圆形头像标签（自绘）
# ============================================================
class AvatarLabel(QLabel):
    """圆形头像标签，用颜色块代替实际图片"""

    def __init__(self, color="#07C160", text="微", size=42, parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.size = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 画圆形背景
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.size, self.size)
        # 画文字
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)
        painter.end()


# ============================================================
# 未读消息红点标签
# ============================================================
class UnreadBadge(QLabel):
    """右上角红色未读小圆点"""

    def __init__(self, count=0, parent=None):
        super().__init__(parent)
        self.count = count
        self.setFixedSize(18, 18)
        self.setAlignment(Qt.AlignCenter)
        if count > 0:
            self.setText(str(count) if count < 100 else "99+")
            self.setStyleSheet("""
                background-color: #fa5151;
                color: #ffffff;
                border-radius: 9px;
                font-size: 10px;
                font-weight: bold;
            """)
        else:
            self.setText("")
            self.setStyleSheet("background: transparent;")


# ============================================================
# 会话列表项 Widget（自定义 QListWidgetItem 的内容）
# ============================================================
class SessionItemWidget(QWidget):
    """会话条目：圆形头像 + 昵称 + 消息预览 + 时间 + 未读红点"""

    def __init__(self, avatar_color, avatar_text, name, preview, time_str, unread=0, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(65)

        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # 左侧：头像
        self.avatar = AvatarLabel(color=avatar_color, text=avatar_text, size=44)
        layout.addWidget(self.avatar)

        # 中间：昵称 + 消息预览
        middle_layout = QVBoxLayout()
        middle_layout.setSpacing(4)

        # 昵称行
        name_layout = QHBoxLayout()
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; background: transparent;")
        name_layout.addWidget(self.name_label)
        name_layout.addStretch()

        # 时间
        self.time_label = QLabel(time_str)
        self.time_label.setStyleSheet("font-size: 11px; color: #999999; background: transparent;")
        name_layout.addWidget(self.time_label)
        middle_layout.addLayout(name_layout)

        # 消息预览
        self.preview_label = QLabel(preview)
        self.preview_label.setStyleSheet("font-size: 12px; color: #999999; background: transparent;")
        self.preview_label.setMaximumWidth(180)
        middle_layout.addWidget(self.preview_label)

        layout.addLayout(middle_layout, stretch=1)

        # 右侧：未读红点
        self.unread_badge = UnreadBadge(unread)
        layout.addWidget(self.unread_badge, alignment=Qt.AlignTop)


# ============================================================
# 聊天消息气泡（仅展示用）
# ============================================================
class ChatBubble(QWidget):
    """聊天消息气泡"""

    def __init__(self, text, is_self=False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)

        if is_self:
            layout.addStretch()
            bubble = QLabel(text)
            bubble.setStyleSheet("""
                background-color: #95ec69;
                color: #333333;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 13px;
                max-width: 400px;
            """)
            bubble.setWordWrap(True)
            layout.addWidget(bubble)
        else:
            avatar = AvatarLabel(color="#10aeff", text="对", size=36)
            layout.addWidget(avatar)
            bubble = QLabel(text)
            bubble.setStyleSheet("""
                background-color: #ffffff;
                color: #333333;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 13px;
                max-width: 400px;
            """)
            bubble.setWordWrap(True)
            layout.addWidget(bubble)
            layout.addStretch()


# ============================================================
# 主窗口
# ============================================================
class WeChatMainWindow(QMainWindow):
    """微信三栏布局主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("微信 - PyQt5 三栏布局")
        self.resize(1100, 700)
        self.setMinimumSize(800, 500)

        # 中心 Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== 水平 QSplitter 三栏 =====
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)  # 分割线宽度
        splitter.setChildrenCollapsible(False)  # 禁止完全折叠

        # 第1栏：左侧导航
        splitter.addWidget(self._create_nav_panel())
        # 第2栏：中间会话列表
        splitter.addWidget(self._create_session_panel())
        # 第3栏：右侧聊天面板
        splitter.addWidget(self._create_chat_panel())

        # 设置初始宽度比例
        splitter.setStretchFactor(0, 0)  # 导航固定
        splitter.setStretchFactor(1, 0)  # 列表固定
        splitter.setStretchFactor(2, 1)  # 聊天区拉伸
        splitter.setSizes([70, 280, 750])

        main_layout.addWidget(splitter)

        # 应用 QSS 样式
        self.setStyleSheet(QSS_STYLE)

    # ----------------------------------------------------------
    # 第1栏：左侧导航面板
    # ----------------------------------------------------------
    def _create_nav_panel(self):
        """创建左侧导航面板：图标按钮垂直排列，底部设置按钮"""
        panel = QWidget()
        panel.setObjectName("navPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(5)

        # 导航按钮配置：(图标文字, 提示)
        nav_buttons = [
            ("💬", "消息"),
            ("👥", "通讯录"),
            ("⭐", "收藏"),
            ("📁", "文件"),
        ]

        self.nav_buttons = []
        for icon, tooltip in nav_buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # 默认选中第一个
        self.nav_buttons[0].setChecked(True)

        # 底部弹簧 + 设置按钮
        layout.addStretch()
        settings_btn = QPushButton("⚙️")
        settings_btn.setToolTip("设置")
        settings_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(settings_btn)

        return panel

    # ----------------------------------------------------------
    # 第2栏：中间会话列表面板
    # ----------------------------------------------------------
    def _create_session_panel(self):
        """创建中间会话列表面板：搜索框 + QListWidget 会话列表"""
        panel = QWidget()
        panel.setObjectName("sessionPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部搜索框
        search_container = QWidget()
        search_container.setStyleSheet("background-color: #f7f7f7; padding: 8px;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 8, 10, 8)

        search_box = QTextEdit()
        search_box.setPlaceholderText("🔍 搜索")
        search_box.setFixedHeight(30)
        search_box.setStyleSheet("""
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            color: #999999;
        """)
        search_layout.addWidget(search_box)
        layout.addWidget(search_container)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e6e6e6; max-height: 1px;")
        layout.addWidget(line)

        # 会话列表
        self.session_list = QListWidget()
        self.session_list.setObjectName("sessionList")
        self.session_list.setSpacing(0)

        # 模拟会话数据
        sessions = [
            ("#07C160", "文", "文件传输助手", "您有一个新文件待接收", "09:30", 2),
            ("#10aeff", "微", "微信团队", "欢迎使用微信", "昨天", 0),
            ("#fa9d3b", "订", "订阅号消息", "3条新消息", "昨天", 3),
            ("#fa5151", "服", "服务通知", "您的订单已发货", "周一", 0),
            ("#9c27b0", "张", "张三", "好的，明天见！", "周一", 0),
            ("#ff9800", "李", "李四", "[图片]", "09/10", 1),
            ("#2196f3", "王", "王五", "收到，谢谢", "09/09", 0),
            ("#4caf50", "赵", "赵六", "周末一起吃饭吗？", "09/08", 5),
            ("#e91e63", "钱", "钱七", "好的没问题", "09/07", 0),
            ("#673ab7", "孙", "孙八", "文件已发送", "09/06", 0),
        ]

        for avatar_color, avatar_text, name, preview, time_str, unread in sessions:
            # 创建自定义 Widget
            item_widget = SessionItemWidget(
                avatar_color=avatar_color,
                avatar_text=avatar_text,
                name=name,
                preview=preview,
                time_str=time_str,
                unread=unread
            )
            # 创建 QListWidgetItem
            list_item = QListWidgetItem(self.session_list)
            list_item.setSizeHint(QSize(0, 65))
            self.session_list.addItem(list_item)
            self.session_list.setItemWidget(list_item, item_widget)

        layout.addWidget(self.session_list, stretch=1)

        return panel

    # ----------------------------------------------------------
    # 第3栏：右侧聊天面板
    # ----------------------------------------------------------
    def _create_chat_panel(self):
        """创建右侧聊天面板：标题栏 + 聊天内容 + 输入栏"""
        panel = QWidget()
        panel.setObjectName("chatPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 顶部标题栏（50px）=====
        title_bar = QWidget()
        title_bar.setObjectName("chatTitle")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)

        # 头像 + 会话名称
        title_avatar = AvatarLabel(color="#07C160", text="文", size=32)
        title_layout.addWidget(title_avatar)

        title_label = QLabel("文件传输助手")
        title_label.setObjectName("chatTitleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # 右侧功能按钮
        for icon in ["📞", "⋯"]:
            btn = QPushButton(icon)
            btn.setStyleSheet("""
                background: transparent;
                border: none;
                font-size: 16px;
                color: #666666;
                min-width: 32px;
                max-width: 32px;
            """)
            btn.setCursor(Qt.PointingHandCursor)
            title_layout.addWidget(btn)

        layout.addWidget(title_bar)

        # ===== 中间聊天内容区域（QScrollArea）=====
        scroll_area = QScrollArea()
        scroll_area.setObjectName("chatContent")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 聊天内容容器
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 10, 0, 10)
        chat_layout.setSpacing(0)
        chat_layout.addStretch()

        # 模拟聊天消息
        messages = [
            ("您好，这是一条测试消息", False),
            ("收到，请问有什么可以帮您？", True),
            ("我想了解一下微信三栏布局的实现方式", False),
            ("好的，三栏布局使用 QSplitter 实现，支持拖拽调整宽度", True),
            ("左侧是导航栏，中间是会话列表，右侧是聊天区域", True),
        ]
        for text, is_self in messages:
            bubble = ChatBubble(text, is_self)
            chat_layout.insertWidget(chat_layout.count() - 1, bubble)

        scroll_area.setWidget(chat_container)
        layout.addWidget(scroll_area, stretch=1)

        # ===== 底部输入栏 =====
        input_panel = QWidget()
        input_panel.setObjectName("chatInput")
        input_layout = QVBoxLayout(input_panel)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)

        # 工具栏：表情按钮等
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(12, 6, 12, 0)
        emoji_btn = QPushButton("😊")
        emoji_btn.setObjectName("emojiBtn")
        emoji_btn.setCursor(Qt.PointingHandCursor)
        toolbar.addWidget(emoji_btn)

        for icon in ["📁", "✂️", "📋"]:
            btn = QPushButton(icon)
            btn.setObjectName("emojiBtn")
            btn.setCursor(Qt.PointingHandCursor)
            toolbar.addWidget(btn)
        toolbar.addStretch()
        input_layout.addLayout(toolbar)

        # 多行输入框
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("输入消息...")
        self.input_box.setMinimumHeight(60)
        self.input_box.setStyleSheet("""
            background-color: #ffffff;
            border: none;
            font-size: 13px;
            color: #333333;
            padding: 8px 12px;
        """)
        input_layout.addWidget(self.input_box, stretch=1)

        # 发送按钮行
        send_row = QHBoxLayout()
        send_row.setContentsMargins(0, 0, 12, 10)
        send_row.addStretch()
        send_btn = QPushButton("发送(S)")
        send_btn.setObjectName("sendBtn")
        send_btn.setCursor(Qt.PointingHandCursor)
        send_row.addWidget(send_btn)
        input_layout.addLayout(send_row)

        layout.addWidget(input_panel)

        return panel


# ============================================================
# 程序入口
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用 Fusion 风格，确保 QSS 生效

    window = WeChatMainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


# ============================================================
# PyInstaller 打包命令：
# ============================================================
# 基础打包（单文件，无控制台窗口）：
#   pyinstaller --onefile --windowed --name WeChatUI wechat_ui.py
#
# 带图标打包：
#   pyinstaller --onefile --windowed --icon=app.ico --name WeChatUI wechat_ui.py
#
# 打包到指定目录：
#   pyinstaller --onefile --windowed --distpath ./dist --name WeChatUI wechat_ui.py
#
# 注意：
#   1. 打包前确保已安装 pyinstaller: pip install pyinstaller
#   2. --windowed 表示不显示控制台黑窗口
#   3. --onefile 表示打包成单个 exe 文件
#   4. 首次运行 exe 会较慢（需要解压），属正常现象
# ============================================================
