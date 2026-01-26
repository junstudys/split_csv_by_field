"""
日期工具类测试
"""

import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 添加src目录到路径
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from src.utils.date_utils import DateUtils  # noqa: E402


class TestDateUtils(unittest.TestCase):
    """测试DateUtils类"""

    def test_detect_date_format_yyyymmdd(self):
        """测试yyyyMMdd格式检测"""
        # 只有纯数字8位应该匹配yyyyMMdd
        self.assertEqual(DateUtils.detect_date_format('20240115'), 'yyyyMMdd')
        self.assertEqual(DateUtils.detect_date_format('19991231'), 'yyyyMMdd')
        # 带分隔符的不应该匹配yyyyMMdd
        self.assertNotEqual(DateUtils.detect_date_format('2024-01-15'), 'yyyyMMdd')
        self.assertNotEqual(DateUtils.detect_date_format('2024/01/15'), 'yyyyMMdd')
        # 带时间的不应该匹配yyyyMMdd
        self.assertNotEqual(DateUtils.detect_date_format('20240115 12:30:00'), 'yyyyMMdd')

    def test_detect_date_format_yyyy_mm_dd(self):
        """测试yyyy-MM-dd格式检测"""
        self.assertEqual(DateUtils.detect_date_format('2024-01-15'), 'yyyy-MM-dd')
        self.assertEqual(DateUtils.detect_date_format('1999-12-31'), 'yyyy-MM-dd')
        # 其他格式不应该匹配yyyy-MM-dd
        self.assertNotEqual(DateUtils.detect_date_format('20240115'), 'yyyy-MM-dd')
        self.assertNotEqual(DateUtils.detect_date_format('2024/01/15'), 'yyyy-MM-dd')

    def test_detect_date_format_yyyy_slash_mm_slash_dd(self):
        """测试yyyy/MM/dd格式检测"""
        self.assertEqual(DateUtils.detect_date_format('2024/01/15'), 'yyyy/MM/dd')
        self.assertEqual(DateUtils.detect_date_format('1999/12/31'), 'yyyy/MM/dd')
        # 其他格式不应该匹配yyyy/MM/dd
        self.assertNotEqual(DateUtils.detect_date_format('2024-01-15'), 'yyyy/MM/dd')

    def test_detect_date_format_yyyymmdd_hhmmss(self):
        """测试yyyyMMdd HH:mm:ss格式检测"""
        self.assertEqual(DateUtils.detect_date_format('20240115 14:30:00'), 'yyyyMMdd HH:mm:ss')
        self.assertEqual(DateUtils.detect_date_format('19991231 23:59:59'), 'yyyyMMdd HH:mm:ss')
        # 其他格式不应该匹配yyyyMMdd HH:mm:ss
        self.assertNotEqual(DateUtils.detect_date_format('2024-01-15 14:30:00'), 'yyyyMMdd HH:mm:ss')

    def test_detect_date_format_yyyy_mm_dd_hhmmss(self):
        """测试yyyy-MM-dd HH:mm:ss格式检测"""
        self.assertEqual(DateUtils.detect_date_format('2024-01-15 14:30:00'), 'yyyy-MM-dd HH:mm:ss')
        self.assertEqual(DateUtils.detect_date_format('1999-12-31 23:59:59'), 'yyyy-MM-dd HH:mm:ss')
        # 其他格式不应该匹配yyyy-MM-dd HH:mm:ss
        self.assertNotEqual(DateUtils.detect_date_format('20240115 14:30:00'), 'yyyy-MM-dd HH:mm:ss')

    def test_detect_date_format_yyyy_slash_mm_slash_dd_hhmmss(self):
        """测试yyyy/MM/dd HH:mm:ss格式检测"""
        self.assertEqual(DateUtils.detect_date_format('2024/01/15 14:30:00'), 'yyyy/MM/dd HH:mm:ss')
        self.assertEqual(DateUtils.detect_date_format('1999/12/31 23:59:59'), 'yyyy/MM/dd HH:mm:ss')
        # 其他格式不应该匹配yyyy/MM/dd HH:mm:ss
        self.assertNotEqual(DateUtils.detect_date_format('2024-01-15 14:30:00'), 'yyyy/MM/dd HH:mm:ss')

    def test_detect_date_format_invalid(self):
        """测试无效日期格式"""
        self.assertIsNone(DateUtils.detect_date_format('not_a_date'))
        self.assertIsNone(DateUtils.detect_date_format('2024-13-01'))  # 无效月份
        self.assertIsNone(DateUtils.detect_date_format('2024-01-32'))  # 无效日期
        self.assertIsNone(DateUtils.detect_date_format(''))

    def test_is_date_column_valid(self):
        """测试有效的日期列检测"""
        series = pd.Series(['20240115', '20240116', '20240117', '20240118', '20240119'])
        self.assertTrue(DateUtils.is_date_column(series))

    def test_is_date_column_below_threshold(self):
        """测试低于阈值的日期列检测"""
        series = pd.Series(['20240115', '20240116', 'invalid', 'invalid', 'invalid'])
        self.assertFalse(DateUtils.is_date_column(series))

    def test_is_date_column_empty(self):
        """测试空列检测"""
        series = pd.Series([])
        self.assertFalse(DateUtils.is_date_column(series))

    def test_is_date_column_all_na(self):
        """测试全NA列检测"""
        series = pd.Series([np.nan, np.nan, np.nan])
        self.assertFalse(DateUtils.is_date_column(series))

    def test_convert_to_datetime_auto(self):
        """测试自动转换日期 - 每种格式单独测试"""
        # 测试yyyyMMdd格式
        series1 = pd.Series(['20240115', '20240116', '20240117'])
        result1 = DateUtils.convert_to_datetime(series1)
        self.assertEqual(result1.isna().sum(), 0)  # 所有值都应该转换成功

        # 测试yyyy-MM-dd格式
        series2 = pd.Series(['2024-01-15', '2024-01-16', '2024-01-17'])
        result2 = DateUtils.convert_to_datetime(series2)
        self.assertEqual(result2.isna().sum(), 0)

        # 测试yyyy/MM/dd格式
        series3 = pd.Series(['2024/01/15', '2024/01/16', '2024/01/17'])
        result3 = DateUtils.convert_to_datetime(series3)
        self.assertEqual(result3.isna().sum(), 0)

    def test_convert_to_datetime_with_na(self):
        """测试包含NA的转换"""
        series = pd.Series(['20240115', np.nan, 'invalid'])
        result = DateUtils.convert_to_datetime(series)
        self.assertTrue(pd.isna(result[1]))  # NaN应该保持NaT
        self.assertTrue(pd.isna(result[2]))  # 无效值应该变成NaT
        self.assertFalse(pd.isna(result[0]))  # 有效值应该转换成功

    def test_get_period_label_year(self):
        """测试年份周期标签"""
        date = pd.Timestamp('2024-01-15')
        self.assertEqual(DateUtils.get_period_label(date, 'Y'), '2024')

    def test_get_period_label_half_year(self):
        """测试半年周期标签"""
        date1 = pd.Timestamp('2024-03-15')
        date2 = pd.Timestamp('2024-09-15')
        self.assertEqual(DateUtils.get_period_label(date1, 'H'), '2024-H1')
        self.assertEqual(DateUtils.get_period_label(date2, 'H'), '2024-H2')

    def test_get_period_label_quarter(self):
        """测试季度周期标签"""
        dates = [
            pd.Timestamp('2024-01-15'),
            pd.Timestamp('2024-04-15'),
            pd.Timestamp('2024-07-15'),
            pd.Timestamp('2024-10-15'),
        ]
        expected = ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4']
        for date, exp in zip(dates, expected):
            self.assertEqual(DateUtils.get_period_label(date, 'Q'), exp)

    def test_get_period_label_month(self):
        """测试月份周期标签"""
        date = pd.Timestamp('2024-03-15')
        self.assertEqual(DateUtils.get_period_label(date, 'M'), '2024-03')

    def test_get_period_label_half_month(self):
        """测试半月周期标签"""
        date1 = pd.Timestamp('2024-01-10')
        date2 = pd.Timestamp('2024-01-20')
        self.assertEqual(DateUtils.get_period_label(date1, 'HM'), '2024-01-HM1')
        self.assertEqual(DateUtils.get_period_label(date2, 'HM'), '2024-01-HM2')

    def test_get_period_label_day(self):
        """测试日周期标签"""
        date = pd.Timestamp('2024-01-15')
        self.assertEqual(DateUtils.get_period_label(date, 'D'), '2024-01-15')

    def test_apply_period_filter_year(self):
        """测试年份周期过滤"""
        dates = pd.to_datetime(['2024-01-15', '2024-06-15', '2025-01-15'])
        result = DateUtils.apply_period_filter(dates, 'Y')
        expected = pd.Series(['2024', '2024', '2025'])
        pd.testing.assert_series_equal(result, expected)

    def test_apply_period_filter_half_year(self):
        """测试半年周期过滤"""
        dates = pd.to_datetime(['2024-03-15', '2024-09-15'])
        result = DateUtils.apply_period_filter(dates, 'H')
        expected = pd.Series(['2024-H1', '2024-H2'])
        pd.testing.assert_series_equal(result, expected)

    def test_apply_period_filter_quarter(self):
        """测试季度周期过滤"""
        dates = pd.to_datetime(['2024-01-15', '2024-04-15', '2024-07-15', '2024-10-15'])
        result = DateUtils.apply_period_filter(dates, 'Q')
        expected = pd.Series(['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'])
        pd.testing.assert_series_equal(result, expected)

    def test_apply_period_filter_month(self):
        """测试月份周期过滤"""
        dates = pd.to_datetime(['2024-01-15', '2024-03-15'])
        result = DateUtils.apply_period_filter(dates, 'M')
        expected = pd.Series(['2024-01', '2024-03'])
        pd.testing.assert_series_equal(result, expected)

    def test_apply_period_filter_half_month(self):
        """测试半月周期过滤"""
        dates = pd.to_datetime(['2024-01-10', '2024-01-20'])
        result = DateUtils.apply_period_filter(dates, 'HM')
        expected = pd.Series(['2024-01-HM1', '2024-01-HM2'])
        pd.testing.assert_series_equal(result, expected)

    def test_apply_period_filter_day(self):
        """测试日周期过滤"""
        dates = pd.to_datetime(['2024-01-15', '2024-01-20'])
        result = DateUtils.apply_period_filter(dates, 'D')
        expected = pd.Series(['2024-01-15', '2024-01-20'])
        pd.testing.assert_series_equal(result, expected)

    def test_apply_period_filter_with_na(self):
        """测试包含NA的周期过滤"""
        dates = pd.to_datetime(['2024-01-15', None, '2024-01-20'])
        result = DateUtils.apply_period_filter(dates, 'D')
        self.assertTrue(pd.isna(result[1]))
        self.assertEqual(result[0], '2024-01-15')
        self.assertEqual(result[2], '2024-01-20')

    def test_validate_time_period_valid(self):
        """测试有效的时间周期验证"""
        for period in ['Y', 'H', 'Q', 'M', 'HM', 'D']:
            self.assertTrue(DateUtils.validate_time_period(period))

    def test_validate_time_period_invalid(self):
        """测试无效的时间周期验证"""
        self.assertFalse(DateUtils.validate_time_period('W'))
        self.assertFalse(DateUtils.validate_time_period('INVALID'))
        self.assertFalse(DateUtils.validate_time_period(''))

    def test_get_time_period_name(self):
        """测试获取时间周期中文名称"""
        self.assertEqual(DateUtils.get_time_period_name('Y'), '年')
        self.assertEqual(DateUtils.get_time_period_name('H'), '半年')
        self.assertEqual(DateUtils.get_time_period_name('Q'), '季度')
        self.assertEqual(DateUtils.get_time_period_name('M'), '月')
        self.assertEqual(DateUtils.get_time_period_name('HM'), '半月')
        self.assertEqual(DateUtils.get_time_period_name('D'), '日')


if __name__ == '__main__':
    unittest.main()
