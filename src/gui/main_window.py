"""
主窗口
提供应用程序的主界面框架
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem, QLabel,
    QSplitter
)
from PyQt6.QtCore import Qt

from .pages.home_page import HomePage
from .pages.file_page import FilePage
from .pages.field_page import FieldPage
from .pages.split_page import SplitPage
from .pages.preview_page import PreviewPage
from .pages.progress_page import ProgressPage
from .pages.result_page import ResultPage
from .pages.settings_page import SettingsPage
from .pages.help_page import HelpPage


class MainWindow(QMainWindow):
    """主窗口"""

    # 页面名称常量
    PAGE_HOME = 'home'
    PAGE_FILE = 'file'
    PAGE_FIELD = 'field'
    PAGE_SPLIT = 'split'
    PAGE_PREVIEW = 'preview'
    PAGE_PROGRESS = 'progress'
    PAGE_RESULT = 'result'
    PAGE_SETTINGS = 'settings'
    PAGE_HELP = 'help'

    def __init__(self, app):
        """
        初始化主窗口

        Args:
            app: CSVSplitterApp 实例
        """
        super().__init__()

        self.app = app
        self.pages = {}

        # 设置窗口
        self.setWindowTitle('CSV 智能拆分工具')
        self.setMinimumSize(1100, 750)  # 增加最小尺寸
        self.resize(1300, 850)

        # 创建中心部件
        self._setup_ui()

        # 连接信号
        self._connect_signals()

        # 加载样式
        self._load_stylesheet()

    def _setup_ui(self):
        """设置 UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 侧边栏
        self.sidebar = self._create_sidebar()
        splitter.addWidget(self.sidebar)

        # 页面容器
        self.page_stack = QStackedWidget()
        splitter.addWidget(self.page_stack)

        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 5)  # 内容区更宽
        splitter.setSizes([180, 1120])  # 调整比例

        main_layout.addWidget(splitter)

        # 创建所有页面
        self._create_pages()

    def _create_sidebar(self):
        """创建侧边栏"""
        sidebar = QWidget()
        sidebar.setObjectName('sidebar')
        sidebar.setMinimumWidth(150)
        sidebar.setMaximumWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # 标题
        title_label = QLabel('CSV 智能拆分工具')
        title_label.setObjectName('sidebarTitle')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        layout.addSpacing(20)

        # 导航列表
        self.nav_list = QListWidget()
        self.nav_list.setObjectName('navList')

        # 添加导航项
        nav_items = [
            ('首页', self.PAGE_HOME),
            ('文件选择', self.PAGE_FILE),
            ('字段配置', self.PAGE_FIELD),
            ('拆分设置', self.PAGE_SPLIT),
            ('预览确认', self.PAGE_PREVIEW),
            ('设置', self.PAGE_SETTINGS),
            ('帮助', self.PAGE_HELP),
        ]

        for text, page_name in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, page_name)
            self.nav_list.addItem(item)

        layout.addWidget(self.nav_list)
        layout.addStretch()

        return sidebar

    def _create_pages(self):
        """创建所有页面"""
        # 首页
        self.pages[self.PAGE_HOME] = HomePage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_HOME])

        # 文件选择页
        self.pages[self.PAGE_FILE] = FilePage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_FILE])

        # 字段配置页
        self.pages[self.PAGE_FIELD] = FieldPage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_FIELD])

        # 拆分设置页
        self.pages[self.PAGE_SPLIT] = SplitPage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_SPLIT])

        # 预览确认页
        self.pages[self.PAGE_PREVIEW] = PreviewPage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_PREVIEW])

        # 进度页
        self.pages[self.PAGE_PROGRESS] = ProgressPage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_PROGRESS])

        # 结果页
        self.pages[self.PAGE_RESULT] = ResultPage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_RESULT])

        # 设置页
        self.pages[self.PAGE_SETTINGS] = SettingsPage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_SETTINGS])

        # 帮助页
        self.pages[self.PAGE_HELP] = HelpPage(self.app, self)
        self.page_stack.addWidget(self.pages[self.PAGE_HELP])

        # 默认显示首页
        self.show_page(self.PAGE_HOME)

    def _connect_signals(self):
        """连接信号"""
        # 导航列表点击
        self.nav_list.itemClicked.connect(self._on_nav_item_clicked)

        # 应用导航信号
        self.app.signals.navigate_to.connect(self.show_page)
        self.app.signals.navigate_next.connect(self._navigate_next)
        self.app.signals.navigate_back.connect(self._navigate_back)

        # 进度页面导航
        self.app.signals.split_started.connect(lambda: self.show_page(self.PAGE_PROGRESS))
        self.app.signals.split_finished.connect(lambda: self.show_page(self.PAGE_RESULT))

    def _on_nav_item_clicked(self, item):
        """导航项点击处理"""
        page_name = item.data(Qt.ItemDataRole.UserRole)
        self.show_page(page_name)

    def _navigate_next(self):
        """导航到下一页"""
        current_page = self.page_stack.currentWidget()
        if hasattr(current_page, 'get_next_page'):
            next_page = current_page.get_next_page()
            if next_page:
                self.show_page(next_page)

    def _navigate_back(self):
        """导航到上一页"""
        current_page = self.page_stack.currentWidget()
        if hasattr(current_page, 'get_prev_page'):
            prev_page = current_page.get_prev_page()
            if prev_page:
                self.show_page(prev_page)

    def show_page(self, page_name):
        """
        显示指定页面

        Args:
            page_name: 页面名称
        """
        if page_name in self.pages:
            page = self.pages[page_name]
            self.page_stack.setCurrentWidget(page)

            # 更新侧边栏选中状态
            for i in range(self.nav_list.count()):
                item = self.nav_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == page_name:
                    self.nav_list.setCurrentItem(item)
                    break

            # 页面激活事件
            if hasattr(page, 'on_activated'):
                page.on_activated()

    def _load_stylesheet(self):
        """加载样式表"""
        # TODO: 从文件加载样式表
        # 暂时使用内联样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }

            #sidebar {
                background-color: #2c3e50;
                color: #ecf0f1;
            }

            #sidebarTitle {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                color: #ecf0f1;
            }

            #navList {
                background-color: transparent;
                border: none;
            }

            #navList::item {
                padding: 12px 20px;
                color: #bdc3c7;
                border-radius: 4px;
            }

            #navList::item:hover {
                background-color: #34495e;
                color: #ecf0f1;
            }

            #navList::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }

            QStackedWidget {
                background-color: #ffffff;
                border-left: 1px solid #ddd;
            }
        """)

    def get_page(self, page_name):
        """
        获取页面实例

        Args:
            page_name: 页面名称

        Returns:
            页面实例
        """
        return self.pages.get(page_name)
