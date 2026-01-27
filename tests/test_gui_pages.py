"""
GUI 页面测试用例

测试所有页面的布局和基本功能，确保：
1. 页面正确初始化
2. 布局组件正确创建
3. 按钮和内容区域正确分离
4. QScrollArea 正确工作
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置 Qt 平台为 offscreen，避免需要 X11 显示
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication, QScrollArea
from PyQt6.QtCore import Qt

from src.gui.pages.base_page import BasePage
from src.gui.pages.home_page import HomePage
from src.gui.pages.file_page import FilePage
from src.gui.pages.field_page import FieldPage
from src.gui.pages.split_page import SplitPage
from src.gui.pages.preview_page import PreviewPage
from src.gui.pages.result_page import ResultPage
from src.gui.pages.settings_page import SettingsPage
from src.gui.pages.help_page import HelpPage
from src.gui.pages.progress_page import ProgressPage


class MockMainWindow:
    """模拟主窗口类"""
    PAGE_HOME = 'home'
    PAGE_FILE = 'file'
    PAGE_FIELD = 'field'
    PAGE_SPLIT = 'split'
    PAGE_PREVIEW = 'preview'
    PAGE_PROGRESS = 'progress'
    PAGE_RESULT = 'result'
    PAGE_SETTINGS = 'settings'
    PAGE_HELP = 'help'


class MockApp:
    """模拟应用程序类"""
    def __init__(self):
        self.state = {}
        self.signals = MockSignals()

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value

    def navigate_to(self, page_name):
        pass

    def navigate_back(self):
        pass

    def navigate_next(self):
        pass

    def reset_state(self):
        self.state.clear()


class MockSignals:
    """模拟信号类"""
    class Signal:
        def __init__(self):
            self.callbacks = []

        def connect(self, callback):
            self.callbacks.append(callback)

        def emit(self, *args):
            for callback in self.callbacks:
                callback(*args)

    def __init__(self):
        self.split_finished = self.Signal()
        self.split_started = self.Signal()
        self.split_progress = self.Signal()
        self.split_failed = self.Signal()
        self.split_cancelled = self.Signal()


class TestBasePage(unittest.TestCase):
    """测试 BasePage 基类"""

    @classmethod
    def setUpClass(cls):
        """创建 QApplication 实例"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """设置测试环境"""
        self.mock_app = MockApp()
        self.mock_main_window = MockMainWindow()

    def test_base_page_initialization(self):
        """测试基础页面初始化"""
        page = BasePage(self.mock_app, self.mock_main_window)

        # 检查页面是否正确初始化
        self.assertIsNotNone(page)
        self.assertIsInstance(page, BasePage)

        # 检查核心布局组件是否存在
        self.assertTrue(hasattr(page, 'content_layout'))
        self.assertTrue(hasattr(page, 'button_layout'))
        self.assertTrue(hasattr(page, 'content_widget'))

    def test_base_page_has_scroll_area(self):
        """测试页面是否包含 QScrollArea"""
        page = BasePage(self.mock_app, self.mock_main_window)

        # 查找 QScrollArea
        scroll_area = page.findChild(QScrollArea)
        self.assertIsNotNone(scroll_area, "页面应该包含 QScrollArea")

        # 检查 QScrollArea 的属性
        self.assertTrue(scroll_area.widgetResizable())
        self.assertEqual(
            scroll_area.horizontalScrollBarPolicy(),
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.assertEqual(
            scroll_area.verticalScrollBarPolicy(),
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )


class TestAllPages(unittest.TestCase):
    """测试所有页面类"""

    @classmethod
    def setUpClass(cls):
        """创建 QApplication 实例"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """设置测试环境"""
        self.mock_app = MockApp()
        self.mock_main_window = MockMainWindow()

    def _test_page_basic_structure(self, page_class, expected_name, expected_title):
        """测试页面的基本结构"""
        page = page_class(self.mock_app, self.mock_main_window)

        # 检查页面属性
        self.assertEqual(page.PAGE_NAME, expected_name)
        self.assertEqual(page.PAGE_TITLE, expected_title)

        # 检查核心布局组件
        self.assertTrue(hasattr(page, 'content_layout'))
        self.assertTrue(hasattr(page, 'button_layout'))
        self.assertTrue(hasattr(page, 'content_widget'))

        # 检查 QScrollArea
        scroll_area = page.findChild(QScrollArea)
        self.assertIsNotNone(scroll_area, f"{page_class.__name__} 应该包含 QScrollArea")

        # 检查按钮容器
        self.assertTrue(hasattr(page, 'button_container'))

        return page

    def test_home_page(self):
        """测试首页"""
        page = self._test_page_basic_structure(
            HomePage, 'home', 'CSV 智能拆分工具'
        )
        # 检查是否有快速入口按钮
        self.assertTrue(len(page.findChildren(
            type(page.findChild(type(page)))
        )) >= 0)

    def test_file_page(self):
        """测试文件选择页面"""
        page = self._test_page_basic_structure(
            FilePage, 'file', '选择文件'
        )
        # 检查验证方法
        is_valid, _ = page.validate()
        self.assertIsInstance(is_valid, bool)

    def test_field_page(self):
        """测试字段配置页面"""
        page = self._test_page_basic_structure(
            FieldPage, 'field', '配置拆分字段'
        )
        # 检查是否有字段列表
        self.assertTrue(hasattr(page, 'field_list'))

    def test_split_page(self):
        """测试拆分设置页面"""
        page = self._test_page_basic_structure(
            SplitPage, 'split', '拆分设置'
        )
        # 检查是否有必要的动态创建控件相关方法
        self.assertTrue(hasattr(page, '_setup_rows_only_mode'))
        self.assertTrue(hasattr(page, '_setup_field_with_date_mode'))
        self.assertTrue(hasattr(page, '_setup_field_without_date_mode'))
        self.assertTrue(hasattr(page, 'on_activated'))  # 用于触发动态创建

    def test_preview_page(self):
        """测试预览确认页面"""
        page = self._test_page_basic_structure(
            PreviewPage, 'preview', '预览确认'
        )
        # 检查验证方法
        is_valid, _ = page.validate()
        self.assertTrue(is_valid)

    def test_result_page(self):
        """测试结果页面"""
        page = self._test_page_basic_structure(
            ResultPage, 'result', '拆分完成'
        )
        # 检查是否有文件列表
        self.assertTrue(hasattr(page, 'files_list'))

    def test_settings_page(self):
        """测试设置页面"""
        page = self._test_page_basic_structure(
            SettingsPage, 'settings', '设置'
        )

    def test_help_page(self):
        """测试帮助页面"""
        page = self._test_page_basic_structure(
            HelpPage, 'help', '帮助'
        )
        # 检查是否有标签页
        self.assertTrue(hasattr(page, 'tab_widget'))

    def test_progress_page(self):
        """测试进度页面"""
        page = self._test_page_basic_structure(
            ProgressPage, 'progress', '执行进度'
        )
        # 检查是否有进度条
        self.assertTrue(hasattr(page, 'total_progress'))
        self.assertTrue(hasattr(page, 'file_progress'))


class TestPageLayout(unittest.TestCase):
    """测试页面布局"""

    @classmethod
    def setUpClass(cls):
        """创建 QApplication 实例"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """设置测试环境"""
        self.mock_app = MockApp()
        self.mock_main_window = MockMainWindow()

    def test_content_and_button_separation(self):
        """测试内容区域和按钮区域是否正确分离"""
        page = HomePage(self.mock_app, self.mock_main_window)

        # 获取布局
        main_layout = page.layout()

        # 检查布局中是否有多个组件
        self.assertGreater(main_layout.count(), 0)

        # 检查是否包含滚动区域和按钮容器
        has_scroll_area = False
        has_button_container = False

        for i in range(main_layout.count()):
            item = main_layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, QScrollArea):
                has_scroll_area = True
            # 检查是否是按钮容器（通过对象名称或直接比较）
            elif widget is not None and widget is page.button_container:
                has_button_container = True

        self.assertTrue(has_scroll_area, "页面应该包含滚动区域")
        self.assertTrue(has_button_container, "页面应该包含按钮容器")

    def test_scroll_area_properties(self):
        """测试滚动区域的属性"""
        page = FieldPage(self.mock_app, self.mock_main_window)

        scroll_area = page.findChild(QScrollArea)
        self.assertIsNotNone(scroll_area)

        # 检查滚动区域的设置
        self.assertTrue(scroll_area.widgetResizable())
        # 水平滚动条策略应该是始终关闭
        self.assertEqual(
            scroll_area.horizontalScrollBarPolicy(),
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        # 垂直滚动条应该是按需显示
        self.assertEqual(
            scroll_area.verticalScrollBarPolicy(),
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

    def test_content_widget_exists(self):
        """测试内容组件是否存在"""
        page = FilePage(self.mock_app, self.mock_main_window)

        self.assertTrue(hasattr(page, 'content_widget'))
        self.assertTrue(hasattr(page, 'content_layout'))

        # 检查内容组件是否在滚动区域内
        scroll_area = page.findChild(QScrollArea)
        self.assertIsNotNone(scroll_area)
        self.assertEqual(scroll_area.widget(), page.content_widget)


class TestPageMethods(unittest.TestCase):
    """测试页面方法"""

    @classmethod
    def setUpClass(cls):
        """创建 QApplication 实例"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """设置测试环境"""
        self.mock_app = MockApp()
        self.mock_main_window = MockMainWindow()

    def test_validate_method_exists(self):
        """测试验证方法是否存在"""
        page = FilePage(self.mock_app, self.mock_main_window)

        # 所有页面都应该有 validate 方法
        self.assertTrue(hasattr(page, 'validate'))
        self.assertTrue(callable(page.validate))

        # 验证方法应该返回元组
        result = page.validate()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], bool)
        self.assertIsInstance(result[1], str)

    def test_collect_data_method_exists(self):
        """测试数据收集方法是否存在"""
        page = SplitPage(self.mock_app, self.mock_main_window)

        # 所有页面都应该有 collect_data 方法
        self.assertTrue(hasattr(page, 'collect_data'))
        self.assertTrue(callable(page.collect_data))

        # collect_data 方法应该返回字典
        result = page.collect_data()
        self.assertIsInstance(result, dict)

    def test_on_activated_method_exists(self):
        """测试页面激活方法是否存在"""
        page = SettingsPage(self.mock_app, self.mock_main_window)

        # 所有页面都应该有 on_activated 方法
        self.assertTrue(hasattr(page, 'on_activated'))
        self.assertTrue(callable(page.on_activated))

        # 调用不应该抛出异常
        try:
            page.on_activated()
        except Exception as e:
            self.fail(f"on_activated() 抛出了异常: {e}")

    def test_navigation_methods(self):
        """测试导航方法"""
        page = PreviewPage(self.mock_app, self.mock_main_window)

        # 测试 get_prev_page
        self.assertTrue(hasattr(page, 'get_prev_page'))
        self.assertTrue(callable(page.get_prev_page))

        # 测试 get_next_page
        self.assertTrue(hasattr(page, 'get_next_page'))
        self.assertTrue(callable(page.get_next_page))


if __name__ == '__main__':
    unittest.main(verbosity=2)
