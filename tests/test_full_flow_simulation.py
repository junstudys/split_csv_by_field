"""
完整流程模拟测试
模拟用户从 FilePage → SplitPage → PreviewPage → Worker 的完整流程
重点关注按行数拆分模式
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
    class Signal:
        def __init__(self):
            self.emitted_values = []

        def emit(self, *args):
            self.emitted_values.append(args)

        def connect(self, callback):
            pass

    def __init__(self):
        self.split_started = self.Signal()
        self.split_finished = self.Signal()


class MockApp:
    """模拟应用程序类"""
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
            'is_folder': False,
            'recursive': False,
        }
        self.signals = MockSignals()

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value


class MockFilePage:
    """模拟 FilePage"""
    def __init__(self, app, main_window):
        self.app = app
        self.main_window = main_window
        # 模拟 UI 控件状态
        self.rows_split_radio_checked = False
        self.field_split_radio_checked = True

    def set_rows_mode(self):
        """用户操作：选择按行数拆分"""
        self.rows_split_radio_checked = True
        self.field_split_radio_checked = False

    def set_field_mode(self):
        """用户操作：选择按字段拆分"""
        self.rows_split_radio_checked = False
        self.field_split_radio_checked = True

    def collect_data(self):
        """收集页面数据"""
        # 模拟 file_page.py 的 collect_data()
        split_type = 'rows' if self.rows_split_radio_checked else 'field'

        # 保存状态
        self.app.set_state('split_type', split_type)

        return {
            'split_type': split_type,
        }

    def get_next_page(self):
        """获取下一页"""
        split_type = self.app.get_state('split_type', 'field')
        if split_type == 'rows':
            return self.main_window.PAGE_SPLIT
        else:
            return self.main_window.PAGE_FIELD


class MockSplitPage:
    """模拟 SplitPage"""
    def __init__(self, app, main_window):
        self.app = app
        self.main_window = main_window
        # 模拟按行数拆分模式的 UI 控件
        self.rows_max_rows_spin_value = 500000
        self.simple_limit_radio_checked = False
        self.simple_max_rows_spin_value = 500000

    def collect_data(self):
        """收集页面数据"""
        # 模拟 split_page.py 的 collect_data()
        split_type = self.app.get_state('split_type', 'field')

        if split_type == 'rows':
            # 按行数拆分模式
            max_rows = self.rows_max_rows_spin_value
            time_period = None
        else:
            # 按字段拆分模式
            date_fields = self.app.get_state('date_fields', [])

            if date_fields:
                # 有日期字段
                if self.app.get_state('enable_time'):
                    time_period = self.app.get_state('time_period', 'M')
                else:
                    time_period = None

                if self.app.get_state('enable_size'):
                    max_rows = self.app.get_state('max_rows', 500000)
                else:
                    max_rows = None
            else:
                # 无日期字段
                if self.simple_limit_radio_checked:
                    max_rows = self.simple_max_rows_spin_value
                else:
                    max_rows = None
                time_period = None

        # 保存状态
        self.app.set_state('time_period', time_period)
        self.app.set_state('max_rows', max_rows)

        return {
            'time_period': time_period,
            'max_rows': max_rows,
        }

    def get_next_page(self):
        """获取下一页"""
        return self.main_window.PAGE_PREVIEW


class MockPreviewPage:
    """模拟 PreviewPage"""
    def __init__(self, app, main_window):
        self.app = app
        self.main_window = main_window

    def get_config(self):
        """获取配置"""
        # 模拟发送给 worker 的配置
        return self.app.state.copy()

    def on_start_clicked(self):
        """开始拆分"""
        config = self.get_config()
        return config


class MockSplitWorker:
    """模拟 SplitWorker"""
    def __init__(self, config):
        self.config = config

    def get_split_method(self):
        """获取应该使用的拆分方法"""
        split_type = self.config.get('split_type', 'field')

        if split_type == 'rows':
            return 'split_by_rows_only'
        else:
            return 'split_single_file'


class TestFullFlowRowsOnly(unittest.TestCase):
    """测试按行数拆分的完整流程"""

    def setUp(self):
        """设置测试环境"""
        self.app = MockApp()
        self.main_window = MockMainWindow()

    def test_rows_only_flow_from_start(self):
        """测试完整的按行数拆分流程"""
        # === 阶段 1: FilePage - 用户选择按行数拆分 ===
        file_page = MockFilePage(self.app, self.main_window)

        # 用户操作：选择按行数拆分
        file_page.set_rows_mode()

        # 用户点击"下一步" - 调用 collect_data()
        file_data = file_page.collect_data()

        # 验证：split_type 已设置
        self.assertEqual(file_data['split_type'], 'rows')
        self.assertEqual(self.app.get_state('split_type'), 'rows')

        # 验证：下一页是 SplitPage（跳过 FieldPage）
        next_page = file_page.get_next_page()
        self.assertEqual(next_page, 'split',
                        "按行数拆分模式下应该跳过 FieldPage")

        # === 阶段 2: SplitPage - 设置行数限制 ===
        split_page = MockSplitPage(self.app, self.main_window)

        # 用户保持默认行数 500000
        # 用户点击"下一步" - 调用 collect_data()
        split_data = split_page.collect_data()

        # 验证：数据正确
        self.assertEqual(split_data['max_rows'], 500000)
        self.assertIsNone(split_data['time_period'])

        # 验证：状态正确保存
        self.assertEqual(self.app.get_state('max_rows'), 500000)
        self.assertIsNone(self.app.get_state('time_period'))

        # 关键验证：split_type 仍然是 'rows'
        self.assertEqual(self.app.get_state('split_type'), 'rows',
                        "split_type 应该保持为 'rows'")

        # === 阶段 3: PreviewPage - 确认配置 ===
        preview_page = MockPreviewPage(self.app, self.main_window)

        # 用户点击"开始拆分"
        config = preview_page.on_start_clicked()

        # === 阶段 4: SplitWorker - 执行拆分 ===
        worker = MockSplitWorker(config)

        # 验证：worker 接收到的配置正确
        self.assertEqual(config['split_type'], 'rows',
                        "Worker 应该接收到 split_type='rows'")
        self.assertEqual(config['max_rows'], 500000)

        # 验证：应该使用正确的方法
        method = worker.get_split_method()
        self.assertEqual(method, 'split_by_rows_only',
                        "应该使用 split_by_rows_only 方法")

    def test_field_mode_flow_from_start(self):
        """测试完整的按字段拆分流程（对比）"""
        # === 阶段 1: FilePage - 用户选择按字段拆分 ===
        file_page = MockFilePage(self.app, self.main_window)

        # 用户保持默认：按字段拆分
        # file_page.set_field_mode()  # 默认就是 field 模式

        # 用户点击"下一步"
        file_data = file_page.collect_data()

        # 验证
        self.assertEqual(file_data['split_type'], 'field')
        self.assertEqual(self.app.get_state('split_type'), 'field')

        # 验证：下一页是 FieldPage
        next_page = file_page.get_next_page()
        self.assertEqual(next_page, 'field',
                        "按字段拆分模式下应该进入 FieldPage")

    def test_switching_from_field_to_rows(self):
        """测试从按字段拆分切换到按行数拆分"""
        # 初始状态：按字段拆分
        self.app.set_state('split_type', 'field')

        # 用户返回 FilePage 并切换到按行数拆分
        file_page = MockFilePage(self.app, self.main_window)
        file_page.set_rows_mode()

        file_data = file_page.collect_data()

        # 验证：split_type 正确更新
        self.assertEqual(self.app.get_state('split_type'), 'rows')

        # 继续到 SplitPage
        split_page = MockSplitPage(self.app, self.main_window)
        split_page.collect_data()

        # 最终验证
        self.assertEqual(self.app.get_state('split_type'), 'rows',
                        "切换后 split_type 应该是 'rows'")

    def test_state_not_cleared_between_pages(self):
        """测试状态在页面切换时不会被清除"""
        # FilePage 设置状态
        file_page = MockFilePage(self.app, self.main_window)
        file_page.set_rows_mode()
        file_page.collect_data()

        split_type_after_file = self.app.get_state('split_type')

        # SplitPage 读取并设置其他状态
        split_page = MockSplitPage(self.app, self.main_window)
        split_page.collect_data()

        # 验证：split_type 仍然存在
        self.assertEqual(self.app.get_state('split_type'), split_type_after_file,
                        "SplitPage.collect_data() 后 split_type 应该保持不变")

    def test_complete_config_for_worker(self):
        """测试传递给 worker 的完整配置"""
        # 完整流程
        file_page = MockFilePage(self.app, self.main_window)
        file_page.set_rows_mode()
        file_page.collect_data()

        # 设置其他必要状态
        self.app.set_state('file_path', '/test/path/orders.csv')
        self.app.set_state('output_dir', './split_data')

        split_page = MockSplitPage(self.app, self.main_window)
        split_page.collect_data()

        # 获取最终配置
        preview_page = MockPreviewPage(self.app, self.main_window)
        config = preview_page.on_start_clicked()

        # 验证所有关键字段
        self.assertEqual(config['split_type'], 'rows')
        self.assertEqual(config['max_rows'], 500000)
        self.assertIsNone(config['time_period'])
        self.assertEqual(config['fields'], [])  # 按行数拆分 fields 为空列表
        self.assertEqual(config['file_path'], '/test/path/orders.csv')
        self.assertEqual(config['output_dir'], './split_data')


class TestPotentialBugs(unittest.TestCase):
    """测试可能存在的 bug"""

    def setUp(self):
        """设置测试环境"""
        self.app = MockApp()
        self.main_window = MockMainWindow()

    def test_split_type_in_collect_data_return(self):
        """测试 FilePage.collect_data() 是否正确返回 split_type"""
        file_page = MockFilePage(self.app, self.main_window)
        file_page.set_rows_mode()

        data = file_page.collect_data()

        # 验证返回的字典包含 split_type
        self.assertIn('split_type', data)
        self.assertEqual(data['split_type'], 'rows')

    def test_split_page_does_not_modify_split_type(self):
        """测试 SplitPage.collect_data() 不会意外修改 split_type"""
        self.app.set_state('split_type', 'rows')

        split_page = MockSplitPage(self.app, self.main_window)
        split_page.collect_data()

        # 验证 split_type 没有被修改
        self.assertEqual(self.app.get_state('split_type'), 'rows',
                        "SplitPage 不应该修改 split_type")

    def test_default_max_rows_value(self):
        """测试默认 max_rows 值"""
        # 新创建的 app 有默认值
        self.assertEqual(self.app.get_state('max_rows'), 500000,
                        "默认 max_rows 应该是 500000")


if __name__ == '__main__':
    unittest.main(verbosity=2)
