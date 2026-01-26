"""
CSV拆分器测试
"""

import unittest
import os
import tempfile
import shutil
import pandas as pd
from pathlib import Path
import sys

# 添加src目录到路径
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from src.splitter.csv_splitter import CSVSplitter  # noqa: E402
from src.utils.file_utils import FileUtils  # noqa: E402


class TestCSVSplitter(unittest.TestCase):
    """测试CSVSplitter类"""

    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, 'output')

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_test_csv(self, filename, data):
        """创建测试CSV文件"""
        filepath = os.path.join(self.test_dir, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        return filepath

    def test_classify_fields_all_normal(self):
        """测试分类：全是普通字段"""
        splitter = CSVSplitter(output_dir=self.output_dir)
        data = {
            '省份': ['广东', '浙江', '江苏'],
            '城市': ['深圳', '杭州', '南京'],
            '金额': [100, 200, 300]
        }
        filepath = self._create_test_csv('test.csv', data)
        df = pd.read_csv(filepath)

        date_fields, non_date_fields = splitter._classify_fields(df, ['省份', '城市'])

        self.assertEqual(len(date_fields), 0)
        self.assertEqual(len(non_date_fields), 2)
        self.assertIn('省份', non_date_fields)
        self.assertIn('城市', non_date_fields)

    def test_classify_fields_with_date(self):
        """测试分类：包含日期字段"""
        splitter = CSVSplitter(output_dir=self.output_dir)
        data = {
            '省份': ['广东', '浙江', '江苏'],
            '订单日期': ['20240115', '20240116', '20240117']
        }
        filepath = self._create_test_csv('test.csv', data)
        df = pd.read_csv(filepath)

        date_fields, non_date_fields = splitter._classify_fields(df, ['省份', '订单日期'])

        self.assertEqual(len(date_fields), 1)
        self.assertEqual(len(non_date_fields), 1)
        self.assertIn('订单日期', date_fields)
        self.assertIn('省份', non_date_fields)

    def test_classify_fields_nonexistent(self):
        """测试分类：包含不存在的字段"""
        splitter = CSVSplitter(output_dir=self.output_dir)
        data = {'省份': ['广东', '浙江']}
        filepath = self._create_test_csv('test.csv', data)
        df = pd.read_csv(filepath)

        date_fields, non_date_fields = splitter._classify_fields(df, ['省份', '不存在的字段'])

        self.assertEqual(len(date_fields), 0)
        self.assertEqual(len(non_date_fields), 1)
        self.assertIn('省份', non_date_fields)

    def test_split_by_size_no_split(self):
        """测试按行数拆分：不拆分"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        df = pd.DataFrame({'id': [1, 2, 3], 'name': ['A', 'B', 'C']})
        result = splitter._split_by_size(df, 'test', '')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 3)  # 3行

        # 验证文件存在
        output_file = os.path.join(self.output_dir, 'test.csv')
        self.assertTrue(os.path.exists(output_file))

    def test_split_by_size_with_split(self):
        """测试按行数拆分：需要拆分"""
        splitter = CSVSplitter(max_rows=2, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        df = pd.DataFrame({'id': [1, 2, 3, 4, 5], 'name': ['A', 'B', 'C', 'D', 'E']})
        result = splitter._split_by_size(df, 'test', '')

        self.assertEqual(len(result), 3)  # 应该分成3个文件
        self.assertEqual(result[0][1], 2)  # 第一个文件2行
        self.assertEqual(result[1][1], 2)  # 第二个文件2行
        self.assertEqual(result[2][1], 1)  # 第三个文件1行

        # 验证文件存在
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_part1.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_part2.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_part3.csv')))

    def test_split_by_non_date(self):
        """测试按普通字段拆分"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '省份': ['广东', '广东', '浙江', '江苏'],
            '城市': ['深圳', '广州', '杭州', '南京'],
            '金额': [100, 200, 300, 400]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['省份'], 'M')

        # 验证输出文件
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_广东.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_浙江.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_江苏.csv')))

    def test_split_by_date(self):
        """测试按日期字段拆分"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '订单日期': ['20240115', '20240116', '20240201', '20240202'],
            '金额': [100, 200, 300, 400]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['订单日期'], 'M')

        # 验证输出文件
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-01.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-02.csv')))

    def test_split_by_non_date_and_date(self):
        """测试按普通字段+日期拆分"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '省份': ['广东', '广东', '浙江', '浙江'],
            '订单日期': ['20240115', '20240201', '20240116', '20240202'],
            '金额': [100, 200, 300, 400]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['省份', '订单日期'], 'M')

        # 验证输出文件
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_广东_2024-01.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_广东_2024-02.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_浙江_2024-01.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_浙江_2024-02.csv')))

    def test_split_by_half_year(self):
        """测试按半年拆分"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '订单日期': ['20240115', '20240615', '20240715', '20241215'],
            '金额': [100, 200, 300, 400]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['订单日期'], 'H')

        # 验证输出文件
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-H1.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-H2.csv')))

    def test_split_by_half_month(self):
        """测试按半月拆分"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '订单日期': ['20240110', '20240120', '20240205', '20240225'],
            '金额': [100, 200, 300, 400]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['订单日期'], 'HM')

        # 验证输出文件
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-01-HM1.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-01-HM2.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-02-HM1.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-02-HM2.csv')))

    def test_split_with_slash_date_format(self):
        """测试斜杠格式日期"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '订单日期': ['2024/01/15', '2024/01/20', '2024/02/05', '2024/02/25'],
            '金额': [100, 200, 300, 400]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['订单日期'], 'M')

        # 验证输出文件
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-01.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-02.csv')))

    def test_split_with_slash_datetime_format(self):
        """测试斜杠+时间格式日期"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '订单日期': ['2024/01/15 14:30:00', '2024/01/20 10:00:00', '2024/02/05 09:15:00'],
            '金额': [100, 200, 300]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['订单日期'], 'M')

        # 验证输出文件
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-01.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'test_2024-02.csv')))

    def test_stats_tracking(self):
        """测试统计信息跟踪"""
        splitter = CSVSplitter(max_rows=None, output_dir=self.output_dir)
        FileUtils.ensure_output_dir(self.output_dir)

        data = {
            '省份': ['广东', '浙江', '江苏'],
            '金额': [100, 200, 300]
        }
        filepath = self._create_test_csv('test.csv', data)

        splitter.split_single_file(filepath, ['省份'], 'M')

        self.assertEqual(splitter.stats['total_files'], 1)
        self.assertEqual(splitter.stats['total_rows'], 3)
        self.assertEqual(splitter.stats['output_files'], 3)
        self.assertEqual(len(splitter.stats['errors']), 0)


if __name__ == '__main__':
    unittest.main()
