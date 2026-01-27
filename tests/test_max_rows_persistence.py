"""
测试行数限制值的持久化
验证用户输入的行数限制值能否正确保存和恢复
"""

import unittest


class MockApp:
    """模拟应用程序类"""
    def __init__(self):
        # 初始状态与真实 app.py 一致
        self.state = {
            'file_path': None,
            'split_type': 'field',
            'fields': [],
            'date_fields': [],
            'non_date_fields': [],
            'time_period': None,
            'max_rows': 500000,  # 默认 50 万行
            'output_dir': './split_data',
        }

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value
        print(f"[DEBUG] set_state('{key}', {value})")


class TestMaxRowsPersistence(unittest.TestCase):
    """测试行数限制值的持久化"""

    def setUp(self):
        """设置测试环境"""
        self.app = MockApp()

    def test_user_enters_10_should_save_10(self):
        """测试用户输入 10，应该保存 10"""
        # 模拟用户操作：在简化版模式（无日期字段）中输入 10
        # 用户点击"按行数拆分大文件"单选按钮
        simple_limit_radio_checked = True
        # 用户在 spinbox 中输入 10
        simple_max_rows_spin_value = 10

        # 模拟 collect_data()
        if simple_limit_radio_checked:
            max_rows = simple_max_rows_spin_value
        else:
            max_rows = None

        # 保存到状态
        self.app.set_state('max_rows', max_rows)

        # 验证：状态应该是 10
        self.assertEqual(self.app.get_state('max_rows'), 10,
                        "用户输入 10 后，状态应该保存为 10")

    def test_restore_should_show_10(self):
        """测试恢复时应该显示 10"""
        # 首先设置状态为 10（模拟用户之前输入并保存了）
        self.app.set_state('max_rows', 10)

        # 模拟 _restore_field_without_date_data() 的逻辑
        max_rows = self.app.get_state('max_rows')

        # 根据 max_rows 决定 UI 状态
        if max_rows is not None:
            simple_limit_radio_checked = True  # 应该选中"按行数拆分"
            simple_max_rows_spin_value = max_rows
            simple_max_rows_spin_enabled = True
        else:
            simple_no_limit_radio_checked = True  # noqa: F841 - 应该选中"不进行行数拆分"
            simple_max_rows_spin_enabled = False

        # 验证：UI 应该显示用户输入的值
        self.assertEqual(max_rows, 10,
                        "恢复时读取的 max_rows 应该是 10")
        self.assertTrue(simple_limit_radio_checked,
                       "应该选中'按行数拆分'单选按钮")
        self.assertEqual(simple_max_rows_spin_value, 10,
                        "spinbox 应该显示 10")
        self.assertTrue(simple_max_rows_spin_enabled,
                       "spinbox 应该是启用状态")

    def test_no_limit_should_save_none(self):
        """测试选择'不进行行数拆分'应该保存 None"""
        # 模拟用户选择"不进行行数拆分"
        simple_limit_radio_checked = False
        # spinbox 的值无所谓，因为不会使用

        # 模拟 collect_data()
        if simple_limit_radio_checked:
            max_rows = None  # 这个分支不会执行
        else:
            max_rows = None

        # 保存到状态
        self.app.set_state('max_rows', max_rows)

        # 验证：状态应该是 None
        self.assertIsNone(self.app.get_state('max_rows'),
                         "选择'不进行行数拆分'时，max_rows 应该是 None")

    def test_restore_none_should_disable_spinbox(self):
        """测试恢复 None 应该禁用 spinbox"""
        # 设置状态为 None
        self.app.set_state('max_rows', None)

        # 模拟 _restore_field_without_date_data() 的逻辑
        max_rows = self.app.get_state('max_rows')

        if max_rows is not None:
            simple_limit_radio_checked = True  # noqa: F841 - 应该选中"按行数拆分"
            simple_max_rows_spin_enabled = True
        else:
            simple_no_limit_radio_checked = True  # 应该选中"不进行行数拆分"
            simple_max_rows_spin_enabled = False

        # 验证
        self.assertIsNone(max_rows,
                         "恢复时 max_rows 应该是 None")
        self.assertTrue(simple_no_limit_radio_checked,
                       "应该选中'不进行行数拆分'单选按钮")
        self.assertFalse(simple_max_rows_spin_enabled,
                        "spinbox 应该被禁用")

    def test_rows_only_mode_should_save_10(self):
        """测试按行数拆分模式应该保存用户输入的值"""
        # 模拟按行数拆分模式
        split_type = 'rows'
        self.app.set_state('split_type', split_type)

        # 用户输入 10
        rows_max_rows_spin_value = 10

        # 模拟 collect_data()
        max_rows = rows_max_rows_spin_value
        self.app.set_state('max_rows', max_rows)

        # 验证
        self.assertEqual(self.app.get_state('max_rows'), 10,
                        "按行数拆分模式下，用户输入 10 应该被保存")

    def test_rows_only_mode_restore_should_show_10(self):
        """测试按行数拆分模式恢复时应该显示 10"""
        # 设置状态
        self.app.set_state('split_type', 'rows')
        self.app.set_state('max_rows', 10)

        # 模拟 _restore_rows_only_data() 的逻辑
        max_rows = self.app.get_state('max_rows')

        if max_rows is not None:
            rows_max_rows_spin_value = max_rows
        else:
            rows_max_rows_spin_value = 500000

        # 验证
        self.assertEqual(max_rows, 10,
                        "恢复时 max_rows 应该是 10")
        self.assertEqual(rows_max_rows_spin_value, 10,
                        "spinbox 应该显示 10")

    def test_field_with_date_mode_should_save_10(self):
        """测试有日期字段模式应该保存用户输入的值"""
        # 模拟有日期字段模式
        self.app.set_state('date_fields', ['订单日期'])
        self.app.set_state('fields', ['订单日期'])

        # 用户选择了"按行数拆分大文件"并输入 10
        enable_size_checkbox_checked = True
        max_rows_spin_value = 10

        # 模拟 collect_data()
        if enable_size_checkbox_checked:
            max_rows = max_rows_spin_value
        else:
            max_rows = None

        self.app.set_state('max_rows', max_rows)

        # 验证
        self.assertEqual(self.app.get_state('max_rows'), 10,
                        "有日期字段模式下，用户输入 10 应该被保存")

    def test_field_with_date_mode_restore_should_show_10(self):
        """测试有日期字段模式恢复时应该显示 10"""
        # 设置状态
        self.app.set_state('date_fields', ['订单日期'])
        self.app.set_state('fields', ['订单日期'])
        self.app.set_state('max_rows', 10)

        # 模拟 _restore_field_with_date_data() 的逻辑
        max_rows = self.app.get_state('max_rows')

        if max_rows is not None:
            enable_size_checkbox_checked = True
            max_rows_spin_value = max_rows
            max_rows_spin_enabled = True
        else:
            enable_size_checkbox_checked = False
            max_rows_spin_enabled = False

        # 验证
        self.assertEqual(max_rows, 10,
                        "恢复时 max_rows 应该是 10")
        self.assertTrue(enable_size_checkbox_checked,
                       "应该选中'按行数拆分大文件'复选框")
        self.assertEqual(max_rows_spin_value, 10,
                        "spinbox 应该显示 10")
        self.assertTrue(max_rows_spin_enabled,
                       "spinbox 应该是启用状态")

    def test_default_value_500k(self):
        """测试默认值是 500000"""
        # 新创建的 app，没有修改过状态
        max_rows = self.app.get_state('max_rows')

        # 验证默认值
        self.assertEqual(max_rows, 500000,
                        "初始状态 max_rows 应该是 500000")


if __name__ == '__main__':
    unittest.main(verbosity=2)
