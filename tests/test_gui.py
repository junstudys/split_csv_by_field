"""
GUI 测试用例
测试 PyQt6 图形界面的各个组件和功能
"""

import sys
import pytest
from pathlib import Path
import tempfile

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PyQt6.QtWidgets import QApplication

# 创建全局 QApplication 实例（pytest-qt 会自动管理）
@pytest.fixture(scope="session")
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


# ==================== 核心应用测试 ====================

class TestCSVSplitterApp:
    """测试应用程序类"""

    def test_app_creation(self, qapp):
        """测试应用程序创建"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        assert app is not None
        assert app.applicationName() == 'CSV 智能拆分工具'
        assert app.signals is not None
        assert app.main_window is not None

    def test_app_state_management(self, qapp):
        """测试应用状态管理"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])

        # 测试设置和获取状态
        app.set_state('test_key', 'test_value')
        assert app.get_state('test_key') == 'test_value'

        # 测试默认值
        assert app.get_state('non_existent', 'default') == 'default'

    def test_app_reset_state(self, qapp):
        """测试状态重置"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])

        # 设置一些状态
        app.set_state('file_path', '/test/path.csv')
        app.set_state('fields', ['field1', 'field2'])

        # 重置
        app.reset_state()

        # 验证重置
        assert app.get_state('file_path') is None
        assert app.get_state('fields') == []


# ==================== 主窗口测试 ====================

class TestMainWindow:
    """测试主窗口"""

    def test_main_window_creation(self, qtbot):
        """测试主窗口创建"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        window = app.main_window

        qtbot.addWidget(window)
        assert window is not None
        assert window.windowTitle() == 'CSV 智能拆分工具'

    def test_page_navigation(self, qtbot):
        """测试页面导航"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        window = app.main_window

        qtbot.addWidget(window)

        # 测试导航到各页面
        pages = [
            window.PAGE_HOME,
            window.PAGE_FILE,
            window.PAGE_FIELD,
            window.PAGE_SPLIT,
            window.PAGE_PREVIEW,
            window.PAGE_SETTINGS,
            window.PAGE_HELP,
        ]

        for page_name in pages:
            window.show_page(page_name)
            assert window.page_stack.currentWidget() == window.pages[page_name]


# ==================== 基础页面测试 ====================

class TestBasePage:
    """测试基础页面"""

    def test_base_page_creation(self, qtbot):
        """测试基础页面创建"""
        from gui.core.app import CSVSplitterApp
        from gui.pages.base_page import BasePage

        app = CSVSplitterApp([])

        # 创建一个测试页面
        class TestPage(BasePage):
            PAGE_NAME = 'test'
            PAGE_TITLE = 'Test Page'

        page = TestPage(app, app.main_window)
        qtbot.addWidget(page)

        assert page.PAGE_NAME == 'test'
        assert page.PAGE_TITLE == 'Test Page'
        assert page.app == app
        assert page.main_window == app.main_window


# ==================== 文件选择页面测试 ====================

class TestFilePage:
    """测试文件选择页面"""

    def test_file_page_creation(self, qtbot):
        """测试文件选择页面创建"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        page = app.main_window.pages[app.main_window.PAGE_FILE]

        qtbot.addWidget(page)
        assert page is not None

    def test_file_page_validation_empty(self, qtbot):
        """测试空路径验证"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        page = app.main_window.pages[app.main_window.PAGE_FILE]

        qtbot.addWidget(page)

        # 空路径应该验证失败
        is_valid, error = page.validate()
        assert not is_valid
        assert '请选择' in error


# ==================== 字段配置页面测试 ====================

class TestFieldPage:
    """测试字段配置页面"""

    def test_field_page_creation(self, qtbot):
        """测试字段配置页面创建"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        page = app.main_window.pages[app.main_window.PAGE_FIELD]

        qtbot.addWidget(page)
        assert page is not None

    def test_field_page_validation_empty(self, qtbot):
        """测试空字段验证"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        page = app.main_window.pages[app.main_window.PAGE_FIELD]

        qtbot.addWidget(page)

        # 没有选择字段应该验证失败
        is_valid, error = page.validate()
        assert not is_valid
        assert '字段' in error


# ==================== 拆分设置页面测试 ====================

class TestSplitPage:
    """测试拆分设置页面"""

    def test_split_page_creation(self, qtbot):
        """测试拆分设置页面创建"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        page = app.main_window.pages[app.main_window.PAGE_SPLIT]

        qtbot.addWidget(page)
        assert page is not None

    def test_split_page_data_collection(self, qtbot):
        """测试数据收集"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        page = app.main_window.pages[app.main_window.PAGE_SPLIT]

        qtbot.addWidget(page)

        # 收集数据
        data = page.collect_data()

        assert 'time_period' in data
        assert 'max_rows' in data
        assert 'output_dir' in data


# ==================== 预览页面测试 ====================

class TestPreviewPage:
    """测试预览确认页面"""

    def test_preview_page_creation(self, qtbot):
        """测试预览页面创建"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        page = app.main_window.pages[app.main_window.PAGE_PREVIEW]

        qtbot.addWidget(page)
        assert page is not None


# ==================== 工作线程测试 ====================

class TestSplitWorker:
    """测试拆分工作线程"""

    @pytest.fixture
    def sample_csv(self):
        """创建示例 CSV 文件"""

        # 创建临时 CSV 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('订单ID,省份,城市,订单日期,金额\n')
            f.write('1,广东,深圳,2024-01-15,100\n')
            f.write('2,广东,广州,2024-01-16,200\n')
            f.write('3,浙江,杭州,2024-02-15,150\n')
            f.write('4,浙江,宁波,2024-02-16,250\n')
            temp_path = f.name

        yield temp_path

        # 清理
        Path(temp_path).unlink(missing_ok=True)

    def test_worker_creation(self, sample_csv):
        """测试工作线程创建"""
        from gui.workers.split_worker import SplitWorker

        config = {
            'file_path': sample_csv,
            'fields': ['省份'],
            'time_period': None,
            'max_rows': None,
            'output_dir': './test_output',
            'encoding': 'auto',
            'is_folder': False,
            'recursive': False,
        }

        worker = SplitWorker(config)
        assert worker is not None
        assert worker.config == config

    def test_worker_execution(self, qtbot, sample_csv):
        """测试工作线程执行"""
        from gui.workers.split_worker import SplitWorker

        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'file_path': sample_csv,
                'fields': ['省份'],
                'time_period': None,
                'max_rows': None,
                'output_dir': tmpdir,
                'encoding': 'auto',
                'is_folder': False,
                'recursive': False,
            }

            worker = SplitWorker(config)

            # 记录结果
            results = {'finished': False, 'error': None}

            def on_finished(result):
                results['finished'] = True
                results['result'] = result

            def on_error(error):
                results['error'] = error

            worker.finished.connect(on_finished)
            worker.error.connect(on_error)

            # 启动工作线程
            worker.start()

            # 等待完成（最多10秒）
            worker.wait(10000)

            # 验证结果
            assert results['finished'] or results['error'] is not None
            if results['finished']:
                assert 'output_files' in results['result']


# ==================== 集成测试 ====================

class TestGUIIntegration:
    """GUI 集成测试"""

    @pytest.fixture
    def sample_csv(self):
        """创建示例 CSV 文件"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('订单ID,省份,城市,订单日期,金额\n')
            f.write('1,广东,深圳,2024-01-15,100\n')
            f.write('2,广东,广州,2024-01-16,200\n')
            f.write('3,浙江,杭州,2024-02-15,150\n')
            f.write('4,浙江,宁波,2024-02-16,250\n')
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink(missing_ok=True)

    def test_complete_workflow(self, qtbot, sample_csv):
        """测试完整工作流"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        window = app.main_window

        qtbot.addWidget(window)

        # 1. 设置文件路径
        app.set_state('file_path', sample_csv)
        app.set_state('is_folder', False)
        app.set_state('encoding', 'auto')

        # 2. 设置字段
        app.set_state('fields', ['省份'])

        # 3. 设置拆分配置
        app.set_state('time_period', None)
        app.set_state('max_rows', None)
        app.set_state('output_dir', './test_output')

        # 验证状态
        assert app.get_state('file_path') == sample_csv
        assert app.get_state('fields') == ['省份']

    def test_page_navigation_workflow(self, qtbot):
        """测试页面导航工作流"""
        from gui.core.app import CSVSplitterApp

        app = CSVSplitterApp([])
        window = app.main_window

        qtbot.addWidget(window)

        # 测试页面顺序
        page_order = [
            window.PAGE_HOME,
            window.PAGE_FILE,
            window.PAGE_FIELD,
            window.PAGE_SPLIT,
            window.PAGE_PREVIEW,
        ]

        current_index = 0
        for page_name in page_order:
            window.show_page(page_name)
            assert window.page_stack.currentIndex() == current_index
            current_index += 1


# ==================== 回归测试：确保CLI功能正常 ====================

class TestCLICompatibility:
    """CLI 兼容性测试"""

    def test_csv_splitter_without_callback(self):
        """测试 CSVSplitter 在没有回调时正常工作"""
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

        from splitter.csv_splitter import CSVSplitter

        # 创建没有回调的拆分器（CLI 模式）
        splitter = CSVSplitter(max_rows=1000, output_dir='./test_output')

        assert splitter.progress_callback is None
        assert splitter.max_rows == 1000
        assert splitter.output_dir == './test_output'

    def test_csv_splitter_with_callback(self):
        """测试 CSVSplitter 带回调正常工作"""
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

        from splitter.csv_splitter import CSVSplitter

        # 创建带回调的拆分器（GUI 模式）
        callback_called = []

        def test_callback(current, total, message):
            callback_called.append((current, total, message))

        splitter = CSVSplitter(
            max_rows=1000,
            output_dir='./test_output',
            progress_callback=test_callback
        )

        assert splitter.progress_callback == test_callback

        # 测试回调
        splitter._emit_progress(50, 100, "Test message")
        assert len(callback_called) == 1
        assert callback_called[0] == (50, 100, "Test message")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
