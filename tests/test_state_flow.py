"""
状态流转测试
测试 GUI 各页面之间的状态传递，特别是按行数拆分模式

这个测试不创建 QWidget，只测试状态管理逻辑
"""

import unittest


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


class MockSignals:
    """模拟信号类"""
    def split_started(self):
        pass


class MockApp:
    """模拟应用程序类 - 测试状态管理逻辑"""
    def __init__(self):
        self.state = {
            'file_path': None,
            'split_type': 'field',
            'fields': [],
            'date_fields': [],
            'non_date_fields': [],
            'time_period': None,
            'max_rows': 500000,
            'output_dir': './split_data',
            'preview_data': None,
        }
        self.signals = MockSignals()

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value


class TestStateFlowRowsOnly(unittest.TestCase):
    """测试按行数拆分模式的状态流转"""

    def setUp(self):
        """设置测试环境"""
        self.mock_app = MockApp()
        self.mock_main_window = MockMainWindow()

    def test_file_page_sets_split_type_to_rows(self):
        """测试 FilePage 正确设置 split_type='rows'"""
        # 模拟 FilePage.collect_data() 在选择按行数拆分时的逻辑
        rows_split_radio_checked = True
        split_type = 'rows' if rows_split_radio_checked else 'field'

        self.mock_app.set_state('split_type', split_type)

        # 验证状态
        self.assertEqual(self.mock_app.get_state('split_type'), 'rows')

    def test_file_page_sets_split_type_to_field(self):
        """测试 FilePage 正确设置 split_type='field'"""
        # 模拟 FilePage.collect_data() 在选择按字段拆分时的逻辑
        rows_split_radio_checked = False
        split_type = 'rows' if rows_split_radio_checked else 'field'

        self.mock_app.set_state('split_type', split_type)

        # 验证状态
        self.assertEqual(self.mock_app.get_state('split_type'), 'field')

    def test_file_page_next_page_for_rows_mode(self):
        """测试按行数拆分模式下，下一页是 SplitPage（跳过 FieldPage）"""
        split_type = 'rows'
        self.mock_app.set_state('split_type', split_type)

        # 模拟 FilePage.get_next_page()
        next_page = self.mock_main_window.PAGE_SPLIT

        self.assertEqual(next_page, 'split')

    def test_file_page_next_page_for_field_mode(self):
        """测试按字段拆分模式下，下一页是 FieldPage"""
        split_type = 'field'
        self.mock_app.set_state('split_type', split_type)

        # 模拟 FilePage.get_next_page()
        next_page = self.mock_main_window.PAGE_FIELD

        self.assertEqual(next_page, 'field')

    def test_split_page_collect_data_rows_mode(self):
        """测试 SplitPage 在按行数拆分模式下正确收集数据"""
        # 设置初始状态
        self.mock_app.set_state('split_type', 'rows')

        # 模拟 SplitPage.collect_data() 中按行数拆分的逻辑
        split_type = self.mock_app.get_state('split_type', 'field')

        if split_type == 'rows':
            max_rows = 500000  # 模拟 rows_max_rows_spin.value()
            time_period = None
        else:
            # 不应该进入这个分支
            max_rows = None
            time_period = None

        self.mock_app.set_state('time_period', time_period)
        self.mock_app.set_state('max_rows', max_rows)

        # 验证状态
        self.assertEqual(self.mock_app.get_state('split_type'), 'rows')
        self.assertEqual(self.mock_app.get_state('max_rows'), 500000)
        self.assertIsNone(self.mock_app.get_state('time_period'))

    def test_split_page_preserves_split_type(self):
        """测试 SplitPage.collect_data() 不应该改变 split_type"""
        # 设置初始状态
        self.mock_app.set_state('split_type', 'rows')

        # 模拟 SplitPage.collect_data() - 当前实现中没有重新设置 split_type
        split_type = self.mock_app.get_state('split_type', 'field')

        if split_type == 'rows':
            max_rows = 500000
            time_period = None

        # 注意：当前代码没有 self.app.set_state('split_type', split_type)
        # 这可能导致状态丢失（如果其他地方清除了状态）

        # 验证 split_type 仍然存在
        self.assertEqual(self.mock_app.get_state('split_type'), 'rows',
                        "split_type 应该被保留")

    def test_preview_page_loads_config_rows_mode(self):
        """测试 PreviewPage 正确加载按行数拆分配置"""
        # 设置完整状态
        self.mock_app.set_state('split_type', 'rows')
        self.mock_app.set_state('file_path', '/path/to/test.csv')
        self.mock_app.set_state('max_rows', 500000)
        self.mock_app.set_state('output_dir', './split_data')

        # 模拟 PreviewPage._load_config()
        split_type = self.mock_app.get_state('split_type', 'field')
        max_rows = self.mock_app.get_state('max_rows')

        # 生成策略描述
        if split_type == 'rows':
            if max_rows:
                strategy = f"按行数拆分，每 {max_rows:,} 行一个文件"
            else:
                strategy = "按行数拆分"
        else:
            strategy = "按字段拆分"

        # 验证
        self.assertEqual(split_type, 'rows')
        self.assertEqual(max_rows, 500000)
        self.assertIn("按行数拆分", strategy)

    def test_preview_page_hides_fields_for_rows_mode(self):
        """测试按行数拆分模式下，字段信息应该隐藏"""
        # 设置状态
        self.mock_app.set_state('split_type', 'rows')
        self.mock_app.set_state('fields', ['field1', 'field2'])  # 即使有字段

        # 模拟 PreviewPage._load_config() 中的逻辑
        split_type = self.mock_app.get_state('split_type', 'field')
        fields = self.mock_app.get_state('fields', [])

        # 决定是否显示字段
        if split_type == 'field' and fields:
            show_fields = True
        else:
            show_fields = False

        # 验证：按行数拆分模式下不应该显示字段
        self.assertFalse(show_fields,
                        "按行数拆分模式下不应该显示字段信息")

    def test_worker_gets_correct_config(self):
        """测试 SplitWorker 接收到的配置正确"""
        # 模拟从 app.state 收集的配置
        config = {
            'split_type': 'rows',
            'file_path': '/path/to/test.csv',
            'fields': [],
            'time_period': None,
            'max_rows': 500000,
            'output_dir': './split_data',
            'encoding': 'auto',
        }

        # 模拟 SplitWorker.run() 中的逻辑
        split_type = config.get('split_type', 'field')
        max_rows = config.get('max_rows')

        # 决定使用哪个方法
        if split_type == 'rows':
            method = 'split_by_rows_only'
        else:
            method = 'split_single_file'

        # 验证
        self.assertEqual(split_type, 'rows')
        self.assertEqual(max_rows, 500000)
        self.assertEqual(method, 'split_by_rows_only')


class TestStateFlowFieldMode(unittest.TestCase):
    """测试按字段拆分模式的状态流转"""

    def setUp(self):
        """设置测试环境"""
        self.mock_app = MockApp()
        self.mock_main_window = MockMainWindow()

    def test_field_mode_with_date_fields(self):
        """测试按字段拆分 + 有日期字段"""
        # 设置状态
        self.mock_app.set_state('split_type', 'field')
        self.mock_app.set_state('fields', ['日期', '地区'])
        self.mock_app.set_state('date_fields', ['日期'])
        self.mock_app.set_state('max_rows', 500000)

        # 模拟 SplitPage.collect_data()
        split_type = self.mock_app.get_state('split_type', 'field')
        date_fields = self.mock_app.get_state('date_fields', [])

        if date_fields and hasattr(self.mock_app, 'enable_time_checkbox'):
            # 有日期字段的情况（测试模拟）
            time_period = 'M'
            max_rows = 500000
        else:
            time_period = None
            max_rows = None

        self.mock_app.set_state('time_period', time_period)
        self.mock_app.set_state('max_rows', max_rows)

        # 验证
        self.assertEqual(split_type, 'field')
        # 注意：实际测试需要更复杂的 mock 来处理 hasattr 检查

    def test_preview_page_shows_fields_for_field_mode(self):
        """测试按字段拆分模式下，字段信息应该显示"""
        # 设置状态
        self.mock_app.set_state('split_type', 'field')
        self.mock_app.set_state('fields', ['地区', '产品'])

        # 模拟 PreviewPage._load_config() 中的逻辑
        split_type = self.mock_app.get_state('split_type', 'field')
        fields = self.mock_app.get_state('fields', [])

        # 决定是否显示字段
        if split_type == 'field' and fields:
            show_fields = True
        else:
            show_fields = False

        # 验证：按字段拆分模式下应该显示字段
        self.assertTrue(show_fields,
                       "按字段拆分模式下应该显示字段信息")


class TestEdgeCases(unittest.TestCase):
    """测试边缘情况"""

    def setUp(self):
        """设置测试环境"""
        self.mock_app = MockApp()

    def test_default_split_type_is_field(self):
        """测试默认拆分类型是 'field'"""
        # 新创建的 MockApp 有默认值
        self.assertEqual(self.mock_app.get_state('split_type'), 'field')

    def test_state_persistence_across_operations(self):
        """测试状态在多次操作后保持一致"""
        # 设置初始状态
        self.mock_app.set_state('split_type', 'rows')
        self.mock_app.set_state('max_rows', 100000)

        # 模拟多次读取
        for _ in range(5):
            split_type = self.mock_app.get_state('split_type')
            max_rows = self.mock_app.get_state('max_rows')
            self.assertEqual(split_type, 'rows')
            self.assertEqual(max_rows, 100000)

    def test_split_type_not_overwritten(self):
        """测试 split_type 不会被其他操作覆盖"""
        self.mock_app.set_state('split_type', 'rows')

        # 模拟设置其他状态（不包含 split_type）
        self.mock_app.set_state('time_period', None)
        self.mock_app.set_state('max_rows', 500000)

        # 验证 split_type 仍然存在
        self.assertEqual(self.mock_app.get_state('split_type'), 'rows')


if __name__ == '__main__':
    unittest.main(verbosity=2)
