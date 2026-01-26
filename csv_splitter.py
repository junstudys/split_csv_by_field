#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV智能拆分工具
功能：按字段、时间周期拆分CSV文件，支持大文件自动二次拆分
版本：v1.3 (优化行数拆分逻辑)
作者：Copilot AI
日期：2025-01-06
"""

import pandas as pd
import os
import shutil
import fire
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import warnings
import chardet

warnings.filterwarnings("ignore")


class DateUtils:
    """日期处理工具类"""
    
    @staticmethod
    def detect_date_format(value):
        """检测日期格式"""
        patterns = {
            'yyyyMMdd': r'^\d{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])$',
            'yyyy-MM-dd': r'^\d{4}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12][0-9]|3[01])$',
            'yyyyMMdd HH:mm:ss': r'^\d{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])\s+([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$',
            'yyyy-MM-dd HH:mm:ss': r'^\d{4}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12][0-9]|3[01])\s+([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'
        }
        
        value_str = str(value).strip()
        for format_name, pattern in patterns.items():
            if re.match(pattern, value_str):
                return format_name
        return None
    
    @staticmethod
    def is_date_column(series, threshold=0.8):
        """
        判断列是否为日期类型
        threshold: 至少多少比例的值符合日期格式
        """
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return False
        
        date_count = sum(1 for x in non_null_series if DateUtils.detect_date_format(x))
        ratio = date_count / len(non_null_series)
        return ratio >= threshold
    
    @staticmethod
    def convert_to_datetime(series):
        """智能转换为datetime"""
        try:
            # 尝试pandas自动解析
            return pd.to_datetime(series, errors='coerce')
        except:
            # 尝试各种格式
            for fmt in ['%Y%m%d', '%Y-%m-%d', '%Y/%m/%d', 
                       '%Y%m%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    return pd.to_datetime(series, format=fmt, errors='coerce')
                except:
                    continue
        return None


class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def detect_encoding(file_path):
        """检测文件编码"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(100000))
            return result['encoding']
    
    @staticmethod
    def safe_filename(name):
        """生成安全的文件名"""
        # 移除或替换不安全字符
        name = str(name).strip()
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in unsafe_chars:
            name = name.replace(char, '_')
        return name[:100]  # 限制长度
    
    @staticmethod
    def get_csv_files(path, recursive=False):
        """获取所有CSV文件"""
        path_obj = Path(path)
        if path_obj.is_file():
            return [path_obj] if path_obj.suffix.lower() == '.csv' else []
        elif path_obj.is_dir():
            pattern = '**/*.csv' if recursive else '*.csv'
            return list(path_obj.glob(pattern))
        return []


class CSVSplitter:
    """CSV拆分核心类"""
    
    def __init__(self, max_rows=None, output_dir='./split_data', encoding='auto'):
        """
        初始化拆分器
        
        Args:
            max_rows: 单文件最大行数
                     - None: 不按行数拆分
                     - 整数: 按指定行数拆分
        """
        self.max_rows = max_rows
        self.output_dir = output_dir
        self.encoding = encoding
        self.stats = {
            'total_files': 0,
            'total_rows': 0,
            'output_files': 0,
            'errors': []
        }
    
    def _prepare_output_dir(self):
        """准备输出目录"""
        if os.path.exists(self.output_dir):
            response = input(f"输出目录 '{self.output_dir}' 已存在，是否清空? (y/n): ")
            if response.lower() == 'y':
                shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _read_csv(self, file_path):
        """读取CSV文件（自动检测编码）"""
        encoding = self.encoding
        if encoding == 'auto':
            encoding = FileUtils.detect_encoding(file_path)
            print(f"  检测到编码: {encoding}")
        
        try:
            return pd.read_csv(file_path, encoding=encoding, low_memory=False)
        except:
            # 尝试常见编码
            for enc in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    return pd.read_csv(file_path, encoding=enc, low_memory=False)
                except:
                    continue
            raise ValueError(f"无法读取文件: {file_path}")
    
    def _split_by_size(self, df, base_name, suffix=''):
        """
        按行数拆分大文件
        
        Args:
            df: DataFrame
            base_name: 基础文件名
            suffix: 文件名后缀
        
        Returns:
            list: [(file_name, row_count), ...]
        """
        output_files = []
        total_rows = len(df)
        
        # ========== 关键修改：根据 max_rows 决定是否拆分 ==========
        if self.max_rows is None or total_rows <= self.max_rows:
            # 不拆分，直接保存整个文件
            file_name = f"{base_name}{suffix}.csv"
            file_path = os.path.join(self.output_dir, file_name)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            output_files.append((file_name, total_rows))
        else:
            # 需要按行数拆分
            num_parts = (total_rows // self.max_rows) + (1 if total_rows % self.max_rows > 0 else 0)
            for i in range(num_parts):
                start_idx = i * self.max_rows
                end_idx = min((i + 1) * self.max_rows, total_rows)
                part_df = df.iloc[start_idx:end_idx]
                
                file_name = f"{base_name}{suffix}_part{i+1}.csv"
                file_path = os.path.join(self.output_dir, file_name)
                part_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                output_files.append((file_name, len(part_df)))
        # ========================================================
        
        return output_files
    
    def _classify_fields(self, df, split_fields):
        """分类字段：日期字段和非日期字段"""
        date_fields = []
        non_date_fields = []
        
        for field in split_fields:
            if field not in df.columns:
                print(f"  ⚠️  警告: 字段 '{field}' 不存在，已跳过")
                continue
            
            if DateUtils.is_date_column(df[field]):
                date_fields.append(field)
                print(f"  ✓ '{field}' 识别为日期字段")
            else:
                non_date_fields.append(field)
                print(f"  ✓ '{field}' 识别为普通字段")
        
        return date_fields, non_date_fields
    
    def _get_period_label(self, period, period_type):
        """获取时间周期标签"""
        period_str = str(period)
        if period_type == 'Y':
            return period_str
        elif period_type == 'Q':
            return period_str.replace('Q', '-Q')
        elif period_type == 'M':
            return period_str
        elif period_type == 'D':
            return period_str
        return period_str
    
    def split_single_file(self, file_path, split_fields, time_period='M'):
        """
        拆分单个CSV文件
        
        Args:
            file_path: 文件路径
            split_fields: 拆分字段列表
            time_period: 时间周期 (Y/Q/M/D)
        """
        print(f"\n{'='*60}")
        print(f"处理文件: {file_path}")
        print(f"{'='*60}")
        
        try:
            # 读取文件
            df = self._read_csv(file_path)
            total_rows = len(df)
            print(f"  总行数: {total_rows:,}")
            print(f"  字段数: {len(df.columns)}")
            
            # ========== 显示行数拆分策略 ==========
            if self.max_rows is None:
                print(f"  行数拆分: ❌ 不拆分（保持完整）")
            else:
                print(f"  行数拆分: ✅ 单文件最大 {self.max_rows:,} 行")
            # =====================================
            
            self.stats['total_files'] += 1
            self.stats['total_rows'] += total_rows
            
            # 分类字段
            date_fields, non_date_fields = self._classify_fields(df, split_fields)
            
            if not date_fields and not non_date_fields:
                print("  ❌ 错误: 没有有效的拆分字段")
                return
            
            # 基础文件名
            base_name = Path(file_path).stem
            output_files = []
            
            # 执行拆分逻辑
            if len(non_date_fields) >= 2:
                # 多个非日期字段：级联拆分
                print(f"\n  拆分策略: 级联拆分 {len(non_date_fields)} 个字段: {non_date_fields}")
                if date_fields:
                    print(f"  附加时间字段: '{date_fields[0]}' (周期: {time_period})")
                    output_files = self._split_multi_fields_with_date(
                        df, base_name, non_date_fields, date_fields[0], time_period
                    )
                else:
                    output_files = self._split_multi_non_date_fields(
                        df, base_name, non_date_fields
                    )
            
            elif non_date_fields and date_fields:
                # 组合拆分：1个非日期字段 + 1个日期字段
                print(f"\n  拆分策略: 按 '{non_date_fields[0]}' + '{date_fields[0]}' (时间周期: {time_period})")
                output_files = self._split_by_non_date_and_date(
                    df, base_name, non_date_fields[0], date_fields[0], time_period
                )
            
            elif non_date_fields:
                # 仅按非日期字段拆分
                print(f"\n  拆分策略: 按 '{non_date_fields[0]}'")
                output_files = self._split_by_non_date(df, base_name, non_date_fields[0])
            
            elif date_fields:
                # 仅按日期字段拆分
                print(f"\n  拆分策略: 按 '{date_fields[0]}' (时间周期: {time_period})")
                output_files = self._split_by_date(df, base_name, date_fields[0], time_period)
            
            # 输出结果统计
            print(f"\n  ✅ 完成! 生成 {len(output_files)} 个文件:")
            for file_name, rows in output_files:
                print(f"     - {file_name} ({rows:,} 行)")
                self.stats['output_files'] += 1
        
        except Exception as e:
            error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            import traceback
            traceback.print_exc()
    
    def _split_multi_non_date_fields(self, df, base_name, fields, current_suffix='', level=0):
        """
        递归按多个非日期字段级联拆分
        
        示例：fields = ['省份', '编码']
        - 第1层：按'省份'拆分 → 广东、浙江、江苏...
        - 第2层：每个省份下按'编码'拆分 → 广东_A001、广东_A002...
        """
        output_files = []
        
        if level >= len(fields):
            # 递归终止：保存文件
            files = self._split_by_size(df, base_name, current_suffix)
            return files
        
        current_field = fields[level]
        unique_values = df[current_field].dropna().unique()
        
        indent = "  " * (level + 2)
        print(f"{indent}第{level+1}层拆分 ('{current_field}'): 找到 {len(unique_values)} 个唯一值")
        
        for value in tqdm(unique_values, desc=f"{indent}拆分中", leave=False):
            sub_df = df[df[current_field] == value]
            safe_value = FileUtils.safe_filename(value)
            new_suffix = f"{current_suffix}_{safe_value}"
            
            # 递归处理下一层
            files = self._split_multi_non_date_fields(
                sub_df, base_name, fields, new_suffix, level + 1
            )
            output_files.extend(files)
        
        return output_files
    
    def _split_multi_fields_with_date(self, df, base_name, non_date_fields, date_field, period_type):
        """
        多非日期字段 + 1个日期字段的级联拆分
        
        示例：['省份', '编码'] + '结算日期'
        - 第1层：按'省份'拆分
        - 第2层：按'编码'拆分
        - 第3层：按'结算日期'时间周期拆分
        """
        output_files = []
        
        def recursive_split(sub_df, suffix, field_index):
            """递归拆分辅助函数"""
            if field_index >= len(non_date_fields):
                # 所有非日期字段处理完毕，按日期拆分
                sub_df[date_field] = DateUtils.convert_to_datetime(sub_df[date_field])
                sub_df_valid = sub_df.dropna(subset=[date_field])
                
                if len(sub_df_valid) > 0:
                    grouped = sub_df_valid.groupby(sub_df_valid[date_field].dt.to_period(period_type))
                    for period, period_df in grouped:
                        period_label = self._get_period_label(period, period_type)
                        final_suffix = f"{suffix}_{period_label}"
                        files = self._split_by_size(period_df, base_name, final_suffix)
                        output_files.extend(files)
                
                # 处理日期为空的数据
                sub_df_null = sub_df[sub_df[date_field].isna()]
                if len(sub_df_null) > 0:
                    final_suffix = f"{suffix}_NULL"
                    files = self._split_by_size(sub_df_null, base_name, final_suffix)
                    output_files.extend(files)
                
                return
            
            # 按当前字段拆分
            current_field = non_date_fields[field_index]
            unique_values = sub_df[current_field].dropna().unique()
            
            indent = "  " * (field_index + 2)
            print(f"{indent}第{field_index+1}层 ('{current_field}'): {len(unique_values)} 个值")
            
            for value in tqdm(unique_values, desc=f"{indent}拆分", leave=False):
                value_df = sub_df[sub_df[current_field] == value]
                safe_value = FileUtils.safe_filename(value)
                new_suffix = f"{suffix}_{safe_value}"
                
                # 递归下一层
                recursive_split(value_df, new_suffix, field_index + 1)
        
        # 开始递归拆分
        recursive_split(df, '', 0)
        return output_files
    
    def _split_by_non_date(self, df, base_name, field):
        """按非日期字段拆分（单个字段）"""
        output_files = []
        unique_values = df[field].dropna().unique()
        
        print(f"     找到 {len(unique_values)} 个唯一值")
        
        for value in tqdm(unique_values, desc="     拆分中"):
            sub_df = df[df[field] == value]
            safe_value = FileUtils.safe_filename(value)
            suffix = f"_{safe_value}"
            
            files = self._split_by_size(sub_df, base_name, suffix)
            output_files.extend(files)
        
        return output_files
    
    def _split_by_date(self, df, base_name, date_field, period_type):
        """按日期字段拆分"""
        output_files = []
        
        # 转换日期
        df[date_field] = DateUtils.convert_to_datetime(df[date_field])
        df_valid = df.dropna(subset=[date_field])
        
        if len(df_valid) == 0:
            print("     ⚠️  警告: 没有有效的日期值")
            return output_files
        
        # 按周期分组
        grouped = df_valid.groupby(df_valid[date_field].dt.to_period(period_type))
        print(f"     找到 {len(grouped)} 个时间周期")
        
        for period, period_df in tqdm(grouped, desc="     拆分中"):
            period_label = self._get_period_label(period, period_type)
            suffix = f"_{period_label}"
            
            files = self._split_by_size(period_df, base_name, suffix)
            output_files.extend(files)
        
        # 处理日期为空的数据
        df_null = df[df[date_field].isna()]
        if len(df_null) > 0:
            print(f"     发现 {len(df_null)} 行日期为空的数据")
            suffix = "_NULL"
            files = self._split_by_size(df_null, base_name, suffix)
            output_files.extend(files)
        
        return output_files
    
    def _split_by_non_date_and_date(self, df, base_name, non_date_field, date_field, period_type):
        """组合拆分：1个非日期字段 + 1个日期字段"""
        output_files = []
        unique_values = df[non_date_field].dropna().unique()
        
        print(f"     第一层拆分: 找到 {len(unique_values)} 个 '{non_date_field}' 值")
        
        for value in tqdm(unique_values, desc="     第一层拆分"):
            sub_df = df[df[non_date_field] == value]
            safe_value = FileUtils.safe_filename(value)
            
            # 转换日期
            sub_df[date_field] = DateUtils.convert_to_datetime(sub_df[date_field])
            sub_df_valid = sub_df.dropna(subset=[date_field])
            
            if len(sub_df_valid) == 0:
                # 如果没有有效日期，直接保存
                suffix = f"_{safe_value}"
                files = self._split_by_size(sub_df, base_name, suffix)
                output_files.extend(files)
                continue
            
            # 按日期周期分组
            grouped = sub_df_valid.groupby(sub_df_valid[date_field].dt.to_period(period_type))
            
            for period, period_df in grouped:
                period_label = self._get_period_label(period, period_type)
                suffix = f"_{safe_value}_{period_label}"
                
                files = self._split_by_size(period_df, base_name, suffix)
                output_files.extend(files)
            
            # 处理该值下日期为空的数据
            sub_df_null = sub_df[sub_df[date_field].isna()]
            if len(sub_df_null) > 0:
                suffix = f"_{safe_value}_NULL"
                files = self._split_by_size(sub_df_null, base_name, suffix)
                output_files.extend(files)
        
        return output_files
    
    def print_summary(self):
        """打印处理摘要"""
        print(f"\n{'='*60}")
        print("处理完成!")
        print(f"{'='*60}")
        print(f"输入文件: {self.stats['total_files']}")
        print(f"总行数: {self.stats['total_rows']:,}")
        print(f"输出文件: {self.stats['output_files']}")
        print(f"输出目录: {os.path.abspath(self.output_dir)}")
        
        if self.stats['errors']:
            print(f"\n⚠️  错误 ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"  - {error}")


class CLI:
    """命令行接口"""
    
    def split(self, 
              input,
              split_fields,
              time_period='M',
              max_rows=None,
              output='./split_data',
              recursive=False,
              encoding='auto'):
        """
        拆分CSV文件
        
        Args:
            input: 输入文件或文件夹路径
            split_fields: 拆分字段，多个字段用逗号分隔（如: "派件网点上级,结算日期"）
            time_period: 时间周期 (Y=年, Q=季度, M=月, D=日)
            max_rows: 单文件最大行数
                     - 不设置: 不按行数拆分
                     - 设置但不给值: 默认50万行
                     - 设置具体值: 按该值拆分
            output: 输出目录
            recursive: 是否递归处理子文件夹
            encoding: 文件编码 (auto/utf-8/gbk等)
        """
        print(f"\n🚀 CSV智能拆分工具 v1.3")
        print(f"{'='*60}")
        print(f"输入路径: {input}")
        print(f"拆分字段: {split_fields}")
        print(f"时间周期: {time_period}")
        
        # ========== 修改：处理 max_rows 参数 ==========
        if max_rows is None:
            print(f"行数拆分: ❌ 不拆分")
            actual_max_rows = None
        elif max_rows is True or max_rows == '':
            # fire库：--max-rows（不带值）会解析为 True
            print(f"行数拆分: ✅ 默认 500,000 行")
            actual_max_rows = 500000
        else:
            actual_max_rows = int(max_rows)
            print(f"行数拆分: ✅ 每 {actual_max_rows:,} 行")
        # =============================================
        
        print(f"输出目录: {output}")
        print(f"{'='*60}")
        
        # 解析字段（兼容字符串和元组）
        if isinstance(split_fields, str):
            fields = [f.strip() for f in split_fields.split(',')]
        elif isinstance(split_fields, (tuple, list)):
            fields = [str(f).strip() for f in split_fields]
        else:
            fields = [str(split_fields).strip()]
        
        print(f"解析后的字段: {fields}\n")
        
        # 获取文件列表
        csv_files = FileUtils.get_csv_files(input, recursive)
        
        if not csv_files:
            print(f"❌ 错误: 在 '{input}' 中未找到CSV文件")
            return
        
        print(f"找到 {len(csv_files)} 个CSV文件\n")
        
        # 初始化拆分器
        splitter = CSVSplitter(max_rows=actual_max_rows, output_dir=output, encoding=encoding)
        splitter._prepare_output_dir()
        
        # 处理每个文件
        for csv_file in csv_files:
            splitter.split_single_file(csv_file, fields, time_period)
        
        # 打印摘要
        splitter.print_summary()
    
    def list_fields(self, file, encoding='auto'):
        """
        列出CSV文件的所有字段
        
        Args:
            file: CSV文件路径
            encoding: 文件编码
        """
        print(f"\n📋 文件字段列表")
        print(f"{'='*60}")
        print(f"文件: {file}")
        
        try:
            if encoding == 'auto':
                encoding = FileUtils.detect_encoding(file)
                print(f"编码: {encoding}")
            
            df = pd.read_csv(file, encoding=encoding, nrows=1000)
            
            print(f"\n总字段数: {len(df.columns)}")
            print(f"{'='*60}")
            
            for i, col in enumerate(df.columns, 1):
                # 检测是否为日期字段
                is_date = DateUtils.is_date_column(df[col])
                col_type = "📅 日期" if is_date else "📝 普通"
                
                # 样例值
                sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else "N/A"
                
                print(f"{i:3d}. {col_type} | {col:30s} | 样例: {sample}")
        
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


def main():
    """主入口"""
    fire.Fire(CLI)


if __name__ == '__main__':
    main()