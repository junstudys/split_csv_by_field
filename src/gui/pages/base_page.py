"""
基础页面类
所有页面的基类，提供通用功能
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt


class BasePage(QWidget):
    """基础页面类"""

    # 页面名称（子类需覆盖）
    PAGE_NAME = ''
    PAGE_TITLE = ''

    def __init__(self, app, main_window):
        """
        初始化页面

        Args:
            app: CSVSplitterApp 实例
            main_window: MainWindow 实例
        """
        super().__init__()

        self.app = app
        self.main_window = main_window
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI（子类可覆盖）"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        # 页面标题
        if self.PAGE_TITLE:
            title_label = QLabel(self.PAGE_TITLE)
            title_label.setObjectName('pageTitle')
            title_label.setStyleSheet("""
                QLabel#pageTitle {
                    font-size: 26px;
                    font-weight: bold;
                    color: #2c3e50;
                }
            """)
            layout.addWidget(title_label)

        # 创建可滚动的内容区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # 设置滚动区域的尺寸策略，让它可以扩展
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(25)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(self.content_widget)

        # 使用 stretch factor：滚动区域占据所有可用空间
        layout.addWidget(scroll_area, stretch=1)

        # 底部按钮区域（在滚动区域之外，固定高度）
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.button_container, stretch=0)

        # 调用子类方法创建内容和按钮
        self._create_content()
        self._create_buttons()

    def _create_content(self):
        """
        创建页面内容（子类需实现）

        子类应该使用 self.content_layout 添加内容组件
        """
        pass

    def _create_buttons(self):
        """
        创建页面按钮（子类可覆盖）

        子类应该使用 self.button_layout 添加按钮
        """
        pass

    def _create_nav_buttons(self, show_back=True, show_next=True, next_text='下一步'):
        """
        创建导航按钮

        Args:
            show_back: 是否显示返回按钮
            show_next: 是否显示下一步按钮
            next_text: 下一步按钮文本
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if show_back:
            back_btn = QPushButton('上一步')
            back_btn.setMinimumWidth(120)
            back_btn.setMinimumHeight(45)
            back_btn.clicked.connect(self._on_back_clicked)
            button_layout.addWidget(back_btn)

        if show_next:
            next_btn = QPushButton(next_text)
            next_btn.setMinimumWidth(120)
            next_btn.setMinimumHeight(45)
            next_btn.setObjectName('primaryButton')
            next_btn.setStyleSheet("""
                QPushButton#primaryButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton#primaryButton:hover {
                    background-color: #2980b9;
                }
                QPushButton#primaryButton:pressed {
                    background-color: #21618c;
                }
            """)
            next_btn.clicked.connect(self._on_next_clicked)
            button_layout.addWidget(next_btn)

        self.button_layout.addLayout(button_layout)

    def _create_card(self, title, content_widget):
        """
        创建卡片容器

        Args:
            title: 卡片标题
            content_widget: 内容组件

        Returns:
            QFrame: 卡片组件
        """
        card = QFrame()
        card.setObjectName('card')
        card.setStyleSheet("""
            QFrame#card {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 25px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            """)
            layout.addWidget(title_label)

            # 分隔线
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet('background-color: #ecf0f1;')
            layout.addWidget(line)

        layout.addWidget(content_widget)

        return card

    def _create_section(self, title, description=''):
        """
        创建区域标题

        Args:
            title: 标题
            description: 描述

        Returns:
            QWidget: 区域组件
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                font-size: 12px;
                color: #7f8c8d;
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        return widget

    def _on_back_clicked(self):
        """返回按钮点击处理"""
        self.app.navigate_back()

    def _on_next_clicked(self):
        """下一步按钮点击处理"""
        # 先验证当前页面输入
        is_valid, error_msg = self.validate()
        if not is_valid:
            # 显示错误提示
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, '输入验证', error_msg)
            return

        # 收集并保存当前页面数据
        self.collect_data()

        # 导航到下一页
        self.app.navigate_next()

    def on_activated(self):
        """页面激活时调用（子类可覆盖）"""
        pass

    def get_next_page(self):
        """
        获取下一页名称（子类可覆盖）

        Returns:
            str: 页面名称或 None
        """
        return None

    def get_prev_page(self):
        """
        获取上一页名称（子类可覆盖）

        Returns:
            str: 页面名称或 None
        """
        return None

    def validate(self):
        """
        验证页面输入（子类可覆盖）

        Returns:
            tuple: (is_valid, error_message)
        """
        return True, ''

    def collect_data(self):
        """
        收集页面数据（子类可覆盖）

        Returns:
            dict: 页面数据
        """
        return {}
