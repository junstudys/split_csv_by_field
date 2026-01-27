"""
首页
应用程序首页，提供快速入口和最近任务
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QGridLayout
)
from PyQt6.QtCore import Qt

from .base_page import BasePage


class HomePage(BasePage):
    """首页"""

    PAGE_NAME = 'home'
    PAGE_TITLE = 'CSV 智能拆分工具'

    def _create_content(self):
        """创建页面内容"""
        # 欢迎区域
        welcome_card = self._create_welcome_section()
        self.content_layout.addWidget(welcome_card)

        # 快速入口
        quick_card = self._create_quick_actions()
        self.content_layout.addWidget(quick_card)

        # 使用提示
        tips_card = self._create_tips_section()
        self.content_layout.addWidget(tips_card)

    def _create_welcome_section(self):
        """创建欢迎区域"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)

        welcome_label = QLabel('欢迎使用 CSV 智能拆分工具')
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        """)
        card_layout.addWidget(welcome_label)

        version_label = QLabel('版本 2.2.0 - 功能强大且易于使用')
        version_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
        """)
        card_layout.addWidget(version_label)

        return self._create_card('', card_content)

    def _create_quick_actions(self):
        """创建快速入口"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)

        title_label = QLabel('快速开始')
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        card_layout.addWidget(title_label)

        # 按钮网格
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # 创建快速入口按钮
        actions = [
            ('选择文件', '选择 CSV 文件开始拆分', self.main_window.PAGE_FILE),
            ('查看帮助', '了解如何使用工具', self.main_window.PAGE_HELP),
            ('设置', '配置默认选项', self.main_window.PAGE_SETTINGS),
        ]

        for i, (title, desc, page) in enumerate(actions):
            btn = self._create_action_button(title, desc, page)
            grid_layout.addWidget(btn, 0, i)

        card_layout.addLayout(grid_layout)

        return self._create_card('', card_content)

    def _create_action_button(self, title, description, page):
        """创建操作按钮"""
        button = QPushButton()
        button.setMinimumHeight(100)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout = QVBoxLayout(button)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            opacity: 0.8;
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # 点击导航
        button.clicked.connect(lambda: self.app.navigate_to(page))

        return button

    def _create_tips_section(self):
        """创建使用提示"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(12)

        title_label = QLabel('使用提示')
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        card_layout.addWidget(title_label)

        # 创建提示容器 - 使用两列布局
        tips_widget = QWidget()
        tips_layout = QGridLayout()
        tips_layout.setSpacing(10)
        tips_layout.setColumnStretch(0, 1)
        tips_layout.setColumnStretch(1, 1)

        tips = [
            ('✓', '支持按日期字段或普通字段拆分'),
            ('✓', '可以级联多个字段进行层级拆分'),
            ('✓', '支持批量处理文件夹'),
            ('✓', '大文件可按行数二次拆分'),
            ('✓', '自动检测文件编码和日期格式'),
            ('⚡', '高效处理百万级数据'),
            ('🔒', '数据安全，本地处理'),
            ('📊', '实时进度显示'),
        ]

        for i, (icon, tip) in enumerate(tips):
            tip_widget = QWidget()
            tip_layout = QHBoxLayout(tip_widget)
            tip_layout.setContentsMargins(8, 8, 8, 8)
            tip_layout.setSpacing(10)

            # 图标标签
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("""
                font-size: 14px;
                color: #3498db;
                min-width: 20px;
            """)
            tip_layout.addWidget(icon_label)

            # 文本标签
            tip_label = QLabel(tip)
            tip_label.setStyleSheet("""
                font-size: 13px;
                color: #34495e;
            """)
            tip_label.setWordWrap(False)
            tip_layout.addWidget(tip_label, 1)

            # 添加到网格布局
            row = i // 2
            col = i % 2
            tips_layout.addWidget(tip_widget, row, col)

        tips_widget.setLayout(tips_layout)
        card_layout.addWidget(tips_widget)

        return self._create_card('', card_content)

    def on_activated(self):
        """页面激活时调用"""
        pass
