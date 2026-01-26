"""
文件工具类测试
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# 添加src目录到路径
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from src.utils.file_utils import FileUtils  # noqa: E402


class TestFileUtils(unittest.TestCase):
    """测试FileUtils类"""

    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_safe_filename_basic(self):
        """测试基本文件名安全处理"""
        self.assertEqual(FileUtils.safe_filename('test.csv'), 'test.csv')
        self.assertEqual(FileUtils.safe_filename('test file'), 'test file')

    def test_safe_filename_unsafe_chars(self):
        """测试不安全字符替换"""
        self.assertEqual(FileUtils.safe_filename('test/file:name'), 'test_file_name')
        self.assertEqual(FileUtils.safe_filename('test*file?.txt'), 'test_file_.txt')
        self.assertEqual(FileUtils.safe_filename('test<file>name'), 'test_file_name')
        self.assertEqual(FileUtils.safe_filename('test|file"name'), 'test_file_name')

    def test_safe_filename_length_limit(self):
        """测试文件名长度限制"""
        long_name = 'a' * 200
        result = FileUtils.safe_filename(long_name)
        self.assertEqual(len(result), 100)

    def test_safe_filename_custom_length(self):
        """测试自定义长度限制"""
        long_name = 'a' * 200
        result = FileUtils.safe_filename(long_name, max_length=50)
        self.assertEqual(len(result), 50)

    def test_safe_filename_empty(self):
        """测试空字符串"""
        result = FileUtils.safe_filename('')
        self.assertEqual(result, '')

    def test_safe_filename_special_values(self):
        """测试特殊值处理"""
        # None
        result = FileUtils.safe_filename(None)
        self.assertEqual(result, 'None')
        # 数字
        result = FileUtils.safe_filename(123)
        self.assertEqual(result, '123')

    def test_get_csv_files_single_file(self):
        """测试获取单个CSV文件"""
        # 创建测试CSV文件
        csv_file = Path(self.test_dir) / 'test.csv'
        csv_file.write_text('id,name\n1,测试')

        result = FileUtils.get_csv_files(str(csv_file))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'test.csv')

    def test_get_csv_files_non_csv(self):
        """测试非CSV文件"""
        txt_file = Path(self.test_dir) / 'test.txt'
        txt_file.write_text('test')

        result = FileUtils.get_csv_files(str(txt_file))
        self.assertEqual(len(result), 0)

    def test_get_csv_files_directory(self):
        """测试获取目录中的CSV文件"""
        # 创建多个CSV文件
        (Path(self.test_dir) / 'test1.csv').write_text('id,name\n1,A')
        (Path(self.test_dir) / 'test2.csv').write_text('id,name\n2,B')
        (Path(self.test_dir) / 'test.txt').write_text('not csv')

        result = FileUtils.get_csv_files(self.test_dir)
        self.assertEqual(len(result), 2)

    def test_get_csv_files_recursive(self):
        """测试递归获取CSV文件"""
        # 创建子目录
        subdir = Path(self.test_dir) / 'subdir'
        subdir.mkdir()

        (Path(self.test_dir) / 'root.csv').write_text('id,name\n1,A')
        (subdir / 'sub.csv').write_text('id,name\n2,B')

        # 不递归
        result = FileUtils.get_csv_files(self.test_dir, recursive=False)
        self.assertEqual(len(result), 1)

        # 递归
        result = FileUtils.get_csv_files(self.test_dir, recursive=True)
        self.assertEqual(len(result), 2)

    def test_get_csv_files_nonexistent_path(self):
        """测试不存在的路径"""
        result = FileUtils.get_csv_files('/nonexistent/path')
        self.assertEqual(len(result), 0)

    def test_ensure_output_dir_create(self):
        """测试创建输出目录"""
        output_dir = os.path.join(self.test_dir, 'new_dir', 'nested')
        FileUtils.ensure_output_dir(output_dir)
        self.assertTrue(os.path.exists(output_dir))

    def test_ensure_output_dir_existing(self):
        """测试已存在的目录"""
        FileUtils.ensure_output_dir(self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))

    def test_get_file_stem(self):
        """测试获取文件名（不含扩展名）"""
        self.assertEqual(FileUtils.get_file_stem('/path/to/file.csv'), 'file')
        self.assertEqual(FileUtils.get_file_stem('file.txt'), 'file')
        self.assertEqual(FileUtils.get_file_stem('file'), 'file')

    def test_format_file_size_bytes(self):
        """测试文件大小格式化"""
        self.assertEqual(FileUtils.format_file_size(500), '500.00 B')
        self.assertEqual(FileUtils.format_file_size(1024), '1.00 KB')
        self.assertEqual(FileUtils.format_file_size(1024 * 1024), '1.00 MB')
        self.assertEqual(FileUtils.format_file_size(1024 * 1024 * 1024), '1.00 GB')

    def test_format_file_size_large(self):
        """测试大文件大小格式化"""
        size = 1.5 * 1024 * 1024 * 1024
        result = FileUtils.format_file_size(size)
        self.assertEqual(result, '1.50 GB')

    def test_write_csv(self):
        """测试写入CSV文件"""
        import pandas as pd

        df = pd.DataFrame({'id': [1, 2, 3], 'name': ['A', 'B', 'C']})
        output_path = os.path.join(self.test_dir, 'output.csv')

        FileUtils.write_csv(df, output_path)

        self.assertTrue(os.path.exists(output_path))
        # 验证内容
        result_df = pd.read_csv(output_path)
        self.assertEqual(len(result_df), 3)


if __name__ == '__main__':
    unittest.main()
