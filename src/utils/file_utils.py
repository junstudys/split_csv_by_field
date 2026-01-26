"""
文件处理工具类
提供编码检测、文件名安全处理、文件枚举等功能
"""

import os
import chardet
from pathlib import Path
from ..utils.constants import (
    SUPPORTED_ENCODINGS,
    UNSAFE_FILENAME_CHARS,
    MAX_FILENAME_LENGTH,
)


class FileUtils:
    """文件处理工具类"""

    @staticmethod
    def detect_encoding(file_path, sample_size=100000):
        """
        检测文件编码

        Args:
            file_path: 文件路径
            sample_size: 用于检测的字节数

        Returns:
            str: 检测到的编码名称
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception:
            return None

    @staticmethod
    def read_csv_with_encoding(file_path, encoding='auto', **kwargs):
        """
        智能读取CSV文件，自动检测或尝试多种编码

        Args:
            file_path: 文件路径
            encoding: 文件编码，'auto' 表示自动检测
            **kwargs: 传递给 pandas.read_csv 的其他参数

        Returns:
            pandas.DataFrame: 读取的数据框
        """
        import pandas as pd

        if encoding == 'auto':
            encoding = FileUtils.detect_encoding(file_path)

        # 尝试指定编码
        if encoding:
            try:
                return pd.read_csv(file_path, encoding=encoding, **kwargs)
            except Exception:
                pass

        # 依次尝试常见编码
        for enc in SUPPORTED_ENCODINGS:
            try:
                return pd.read_csv(file_path, encoding=enc, **kwargs)
            except Exception:
                continue

        raise ValueError(f"无法读取文件: {file_path}，尝试了所有编码均失败")

    @staticmethod
    def safe_filename(name, max_length=None):
        """
        生成安全的文件名

        Args:
            name: 原始名称
            max_length: 最大长度，默认使用 MAX_FILENAME_LENGTH

        Returns:
            str: 安全的文件名
        """
        if max_length is None:
            max_length = MAX_FILENAME_LENGTH

        # 转换为字符串并去除首尾空格
        name = str(name).strip()

        # 替换不安全字符
        for char in UNSAFE_FILENAME_CHARS:
            name = name.replace(char, '_')

        # 限制长度
        return name[:max_length]

    @staticmethod
    def get_csv_files(path, recursive=False):
        """
        获取指定路径下的所有CSV文件

        Args:
            path: 文件或文件夹路径
            recursive: 是否递归搜索子文件夹

        Returns:
            list: Path 对象列表
        """
        path_obj = Path(path)

        if path_obj.is_file():
            return [path_obj] if path_obj.suffix.lower() == '.csv' else []

        elif path_obj.is_dir():
            pattern = '**/*.csv' if recursive else '*.csv'
            return list(path_obj.glob(pattern))

        return []

    @staticmethod
    def prepare_output_dir(output_dir, clear_if_exists=False, ask_user=True):
        """
        准备输出目录

        Args:
            output_dir: 输出目录路径
            clear_if_exists: 目录存在时是否清空
            ask_user: 是否询问用户

        Returns:
            bool: 是否成功准备
        """
        if os.path.exists(output_dir):
            if clear_if_exists:
                if ask_user:
                    response = input(f"输出目录 '{output_dir}' 已存在，是否清空? (y/n): ")
                    if response.lower() != 'y':
                        return False
                import shutil
                shutil.rmtree(output_dir)
        else:
            os.makedirs(output_dir, exist_ok=True)
        return True

    @staticmethod
    def ensure_output_dir(output_dir):
        """
        确保输出目录存在（不询问用户）

        Args:
            output_dir: 输出目录路径
        """
        os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def write_csv(df, file_path, encoding='utf-8-sig'):
        """
        写入CSV文件

        Args:
            df: pandas DataFrame
            file_path: 输出文件路径
            encoding: 文件编码
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir:
            FileUtils.ensure_output_dir(output_dir)

        df.to_csv(file_path, index=False, encoding=encoding)

    @staticmethod
    def get_file_stem(file_path):
        """
        获取文件名（不含扩展名）

        Args:
            file_path: 文件路径

        Returns:
            str: 文件名（不含扩展名）
        """
        return Path(file_path).stem

    @staticmethod
    def format_file_size(size_bytes):
        """
        格式化文件大小

        Args:
            size_bytes: 字节数

        Returns:
            str: 格式化后的大小 (如: "1.23 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
