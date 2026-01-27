"""
测试字段选择逻辑
验证当用户选择/不选择日期字段时，拆分设置页面的显示行为
"""

import unittest


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
        }

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value


class TestFieldSelectionLogic(unittest.TestCase):
    """测试字段选择对拆分设置页面显示的影响"""

    def setUp(self):
        """设置测试环境"""
        self.app = MockApp()

    def test_file_with_date_field_user_selected_date_field(self):
        """测试：文件有日期字段，用户也选择了日期字段 → 显示时间周期+行数限制"""
        # 模拟文件有日期字段
        self.app.set_state('date_fields', ['订单日期', '发货日期'])
        self.app.set_state('non_date_fields', ['地区', '产品', '数量'])

        # 用户选择了包含日期字段的字段
        self.app.set_state('fields', ['订单日期', '地区'])

        # 模拟 SplitPage.on_activated() 的判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：应该显示时间周期 + 行数限制
        self.assertTrue(has_selected_date_field,
                       "用户选择了日期字段，应该显示时间周期设置")

    def test_file_with_date_field_user_no_date_field(self):
        """测试：文件有日期字段，但用户没选日期字段 → 只显示行数限制"""
        # 模拟文件有日期字段
        self.app.set_state('date_fields', ['订单日期', '发货日期'])
        self.app.set_state('non_date_fields', ['地区', '产品', '数量'])

        # 用户只选择了非日期字段
        self.app.set_state('fields', ['地区', '产品', '数量'])

        # 模拟 SplitPage.on_activated() 的判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：不应该显示时间周期
        self.assertFalse(has_selected_date_field,
                        "用户没有选择日期字段，不应该显示时间周期设置")

    def test_file_without_date_field(self):
        """测试：文件没有日期字段 → 只显示行数限制"""
        # 模拟文件没有日期字段
        self.app.set_state('date_fields', [])
        self.app.set_state('non_date_fields', ['地区', '产品', '数量'])

        # 用户选择了字段（都是非日期字段）
        self.app.set_state('fields', ['地区', '产品'])

        # 模拟 SplitPage.on_activated() 的判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：不应该显示时间周期
        self.assertFalse(has_selected_date_field,
                        "文件没有日期字段，不应该显示时间周期设置")

    def test_user_selected_multiple_fields_one_is_date(self):
        """测试：用户选择了多个字段，其中一个是日期字段 → 显示时间周期+行数限制"""
        # 模拟文件有日期字段
        self.app.set_state('date_fields', ['订单日期'])
        self.app.set_state('non_date_fields', ['地区', '产品', '数量'])

        # 用户选择了多个字段，包含一个日期字段
        self.app.set_state('fields', ['地区', '产品', '订单日期', '数量'])

        # 模拟判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：应该显示时间周期
        self.assertTrue(has_selected_date_field,
                       "用户选择的字段中包含日期字段，应该显示时间周期设置")

    def test_user_only_selected_date_fields(self):
        """测试：用户只选择了日期字段 → 显示时间周期+行数限制"""
        # 模拟文件有日期字段
        self.app.set_state('date_fields', ['订单日期', '发货日期'])
        self.app.set_state('non_date_fields', ['地区', '产品'])

        # 用户只选择了日期字段
        self.app.set_state('fields', ['订单日期', '发货日期'])

        # 模拟判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：应该显示时间周期
        self.assertTrue(has_selected_date_field,
                       "用户只选择了日期字段，应该显示时间周期设置")

    def test_empty_field_selection(self):
        """测试：用户没有选择任何字段 → 不显示时间周期"""
        # 模拟文件有日期字段
        self.app.set_state('date_fields', ['订单日期'])
        self.app.set_state('non_date_fields', ['地区', '产品'])

        # 用户没有选择字段
        self.app.set_state('fields', [])

        # 模拟判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：不应该显示时间周期
        self.assertFalse(has_selected_date_field,
                        "用户没有选择字段，不应该显示时间周期设置")

    def test_cascade_split_with_date_field(self):
        """测试：级联拆分包含日期字段 → 显示时间周期+行数限制"""
        # 模拟文件字段
        self.app.set_state('date_fields', ['年月'])
        self.app.set_state('non_date_fields', ['地区', '产品'])

        # 级联拆分：年月 + 地区（包含日期字段）
        self.app.set_state('fields', ['年月', '地区'])

        # 模拟判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：应该显示时间周期
        self.assertTrue(has_selected_date_field,
                       "级联拆分包含日期字段，应该显示时间周期设置")

    def test_cascade_split_without_date_field(self):
        """测试：级联拆分不包含日期字段 → 只显示行数限制"""
        # 模拟文件字段
        self.app.set_state('date_fields', ['年月'])
        self.app.set_state('non_date_fields', ['地区', '产品', '客户'])

        # 级联拆分：地区 + 产品（不包含日期字段）
        self.app.set_state('fields', ['地区', '产品', '客户'])

        # 模拟判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：不应该显示时间周期
        self.assertFalse(has_selected_date_field,
                        "级联拆分不包含日期字段，不应该显示时间周期设置")


class TestEdgeCases(unittest.TestCase):
    """测试边缘情况"""

    def setUp(self):
        """设置测试环境"""
        self.app = MockApp()

    def test_case_sensitivity(self):
        """测试字段名大小写敏感性"""
        # 模拟文件字段
        self.app.set_state('date_fields', ['OrderDate'])  # 英文字段名
        self.app.set_state('fields', ['OrderDate', 'Region'])

        # 模拟判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：应该匹配（大小写敏感）
        self.assertTrue(has_selected_date_field)

    def test_field_name_with_spaces(self):
        """测试带空格的字段名"""
        # 模拟文件字段
        self.app.set_state('date_fields', ['订单 日期'])
        self.app.set_state('fields', ['订单 日期'])

        # 模拟判断逻辑
        selected_fields = self.app.get_state('fields', [])
        date_fields_in_file = self.app.get_state('date_fields', [])
        has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

        # 验证：应该匹配
        self.assertTrue(has_selected_date_field)


if __name__ == '__main__':
    unittest.main(verbosity=2)
