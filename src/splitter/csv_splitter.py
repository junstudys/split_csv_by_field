"""
CSV 拆分核心类
提供按字段、时间周期拆分CSV文件的核心功能
"""

import os
from tqdm import tqdm
from ..utils.date_utils import DateUtils
from ..utils.file_utils import FileUtils
from ..utils.constants import TIME_PERIOD_DESCRIPTIONS


class CSVSplitter:
    """CSV 拆分核心类"""

    def __init__(self, max_rows=None, output_dir='./split_data', encoding='auto', progress_callback=None):
        """
        初始化拆分器

        Args:
            max_rows: 单文件最大行数
                - None: 不按行数拆分
                - 整数: 按指定行数拆分
            output_dir: 输出目录
            encoding: 文件编码 ('auto' 表示自动检测)
            progress_callback: 进度回调函数 (current, total, message) -> None
                - None: 不使用回调（CLI模式，使用tqdm）
                - 函数: GUI模式，通过回调发送进度更新
        """
        self.max_rows = max_rows
        self.output_dir = output_dir
        self.encoding = encoding
        self.progress_callback = progress_callback
        self._reset_stats()

    def _reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_files': 0,
            'total_rows': 0,
            'output_files': 0,
            'output_file_list': [],  # 记录实际生成的文件列表 (file_name, row_count)
            'errors': [],
        }

    def _emit_progress(self, current, total, message):
        """
        发送进度更新（兼容 CLI 和 GUI）

        Args:
            current: 当前进度值
            total: 总值
            message: 进度消息
        """
        if self.progress_callback:
            self.progress_callback(current, total, message)
        # CLI 模式：tqdm 会自动处理进度显示

    def _classify_fields(self, df, split_fields):
        """
        分类字段：日期字段和非日期字段

        Args:
            df: pandas DataFrame
            split_fields: 要拆分的字段列表

        Returns:
            tuple: (date_fields, non_date_fields)
        """
        date_fields = []
        non_date_fields = []

        for field in split_fields:
            if field not in df.columns:
                print(f"  ⚠️  警告: 字段 '{field}' 不存在，已跳过")
                continue

            if DateUtils.is_date_column(df[field]):
                date_fields.append(field)
                print(f"  ✓ '{field}' 识别为 📅 日期字段")
            else:
                non_date_fields.append(field)
                print(f"  ✓ '{field}' 识别为 📝 普通字段")

        return date_fields, non_date_fields

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

        # 判断是否需要拆分
        if self.max_rows is None or total_rows <= self.max_rows:
            # 不拆分，直接保存整个文件
            file_name = f"{base_name}{suffix}.csv"
            file_path = os.path.join(self.output_dir, file_name)
            FileUtils.write_csv(df, file_path)
            output_files.append((file_name, total_rows))
            # 记录到统计
            self.stats['output_file_list'].append((file_name, total_rows))
            self.stats['output_files'] += 1
        else:
            # 需要按行数拆分
            num_parts = (total_rows // self.max_rows) + (1 if total_rows % self.max_rows > 0 else 0)
            for i in range(num_parts):
                start_idx = i * self.max_rows
                end_idx = min((i + 1) * self.max_rows, total_rows)
                part_df = df.iloc[start_idx:end_idx]

                file_name = f"{base_name}{suffix}_part{i + 1}.csv"
                file_path = os.path.join(self.output_dir, file_name)
                FileUtils.write_csv(part_df, file_path)
                output_files.append((file_name, len(part_df)))
                # 记录到统计
                self.stats['output_file_list'].append((file_name, len(part_df)))
                self.stats['output_files'] += 1

        return output_files

    def _split_multi_non_date_fields(self, df, base_name, fields, current_suffix='', level=0):
        """
        递归按多个非日期字段级联拆分

        示例：fields = ['省份', '城市']
        - 第1层：按'省份'拆分 → 广东、浙江、江苏...
        - 第2层：每个省份下按'城市'拆分 → 广东_深圳、广东_广州...

        Args:
            df: DataFrame
            base_name: 基础文件名
            fields: 字段列表
            current_suffix: 当前后缀
            level: 当前层级

        Returns:
            list: [(file_name, row_count), ...]
        """
        output_files = []

        if level >= len(fields):
            # 递归终止：保存文件
            return self._split_by_size(df, base_name, current_suffix)

        current_field = fields[level]
        unique_values = df[current_field].dropna().unique()

        indent = "  " * (level + 2)
        print(f"{indent}第{level + 1}层 ('{current_field}'): 找到 {len(unique_values)} 个唯一值")

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

        示例：['省份', '城市'] + '订单日期'
        - 第1层：按'省份'拆分
        - 第2层：按'城市'拆分
        - 第3层：按'订单日期'时间周期拆分

        Args:
            df: DataFrame
            base_name: 基础文件名
            non_date_fields: 非日期字段列表
            date_field: 日期字段名
            period_type: 时间周期类型

        Returns:
            list: [(file_name, row_count), ...]
        """
        output_files = []

        def recursive_split(sub_df, suffix, field_index):
            """递归拆分辅助函数"""
            if field_index >= len(non_date_fields):
                # 所有非日期字段处理完毕，按日期拆分
                sub_df[date_field] = DateUtils.convert_to_datetime(sub_df[date_field])
                sub_df_valid = sub_df.dropna(subset=[date_field])

                if len(sub_df_valid) > 0:
                    # 应用时间周期过滤
                    period_keys = DateUtils.apply_period_filter(sub_df_valid[date_field], period_type)
                    grouped = sub_df_valid.groupby(period_keys)

                    for period_label, period_df in grouped:
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
            print(f"{indent}第{field_index + 1}层 ('{current_field}'): {len(unique_values)} 个值")

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
        """
        按非日期字段拆分（单个字段）

        Args:
            df: DataFrame
            base_name: 基础文件名
            field: 字段名

        Returns:
            list: [(file_name, row_count), ...]
        """
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
        """
        按日期字段拆分

        Args:
            df: DataFrame
            base_name: 基础文件名
            date_field: 日期字段名
            period_type: 时间周期类型

        Returns:
            list: [(file_name, row_count), ...]
        """
        output_files = []

        # 转换日期
        df[date_field] = DateUtils.convert_to_datetime(df[date_field])
        df_valid = df.dropna(subset=[date_field])

        if len(df_valid) == 0:
            print("     ⚠️  警告: 没有有效的日期值")
            return output_files

        # 按周期分组
        period_keys = DateUtils.apply_period_filter(df_valid[date_field], period_type)
        grouped = df_valid.groupby(period_keys)
        print(f"     找到 {len(grouped)} 个时间周期")

        for period_label, period_df in tqdm(grouped, desc="     拆分中"):
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
        """
        组合拆分：1个非日期字段 + 1个日期字段

        Args:
            df: DataFrame
            base_name: 基础文件名
            non_date_field: 非日期字段名
            date_field: 日期字段名
            period_type: 时间周期类型

        Returns:
            list: [(file_name, row_count), ...]
        """
        output_files = []
        unique_values = df[non_date_field].dropna().unique()

        print(f"     第一层拆分: 找到 {len(unique_values)} 个 '{non_date_field}' 值")

        for value in tqdm(unique_values, desc="     第一层拆分"):
            sub_df = df[df[non_date_field] == value].copy()
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
            period_keys = DateUtils.apply_period_filter(sub_df_valid[date_field], period_type)
            grouped = sub_df_valid.groupby(period_keys)

            for period_label, period_df in grouped:
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

    def split_by_rows_only(self, file_path):
        """
        只按行数拆分CSV文件（不按字段拆分）

        Args:
            file_path: 文件路径
        """
        print(f"\n{'=' * 60}")
        print(f"处理文件: {file_path}")
        print(f"{'=' * 60}")
        print("  拆分模式: 按行数拆分")

        # 发送进度：开始处理
        self._emit_progress(0, 100, f"开始处理: {file_path}")

        try:
            # 读取文件
            self._emit_progress(10, 100, "读取文件...")
            df = FileUtils.read_csv_with_encoding(file_path, encoding=self.encoding, low_memory=False)
            total_rows = len(df)
            print(f"  总行数: {total_rows:,}")
            print(f"  字段数: {len(df.columns)}")

            # 必须设置 max_rows
            if self.max_rows is None:
                print("  ❌ 错误: 按行数拆分模式必须设置 max_rows 参数")
                self._emit_progress(100, 100, "处理失败：未设置 max_rows")
                return

            print(f"  行数拆分: ✅ 单文件最大 {self.max_rows:,} 行")

            self.stats['total_files'] += 1
            self.stats['total_rows'] += total_rows

            # 基础文件名
            base_name = FileUtils.get_file_stem(file_path)

            # 执行按行数拆分
            self._emit_progress(30, 100, "开始拆分...")
            print("\n  拆分策略: 按行数拆分（不进行字段分类）")

            output_files = self._split_by_size(df, base_name, suffix='')

            # 输出结果统计
            self._emit_progress(90, 100, "完成拆分")
            actual_output_count = len(self.stats['output_file_list'])
            print(f"\n  ✅ 完成! 生成 {actual_output_count} 个文件:")
            for file_name, rows in output_files:
                print(f"     - {file_name} ({rows:,} 行)")

            self._emit_progress(100, 100, f"完成! 生成 {actual_output_count} 个文件")

        except Exception as e:
            error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
            print(f"  ❌ {error_msg}")
            self._emit_progress(100, 100, f"错误: {error_msg}")
            self.stats['errors'].append(error_msg)
            import traceback
            traceback.print_exc()

    def split_single_file(self, file_path, split_fields, time_period=None):
        """
        拆分单个CSV文件

        Args:
            file_path: 文件路径
            split_fields: 拆分字段列表
            time_period: 时间周期 (Y/H/Q/M/HM/D)，None 表示不使用时间周期拆分
        """
        print(f"\n{'=' * 60}")
        print(f"处理文件: {file_path}")
        print(f"{'=' * 60}")

        # 发送进度：开始处理
        self._emit_progress(0, 100, f"开始处理: {file_path}")

        try:
            # 读取文件
            self._emit_progress(10, 100, "读取文件...")
            df = FileUtils.read_csv_with_encoding(file_path, encoding=self.encoding, low_memory=False)
            total_rows = len(df)
            print(f"  总行数: {total_rows:,}")
            print(f"  字段数: {len(df.columns)}")

            # 显示行数拆分策略
            if self.max_rows is None:
                print("  行数拆分: ❌ 不拆分（保持完整）")
            else:
                print(f"  行数拆分: ✅ 单文件最大 {self.max_rows:,} 行")

            self.stats['total_files'] += 1
            self.stats['total_rows'] += total_rows

            # 分类字段
            self._emit_progress(20, 100, "分析字段...")
            date_fields, non_date_fields = self._classify_fields(df, split_fields)

            if not date_fields and not non_date_fields:
                print("  ❌ 错误: 没有有效的拆分字段")
                self._emit_progress(100, 100, "处理失败：没有有效字段")
                return

            # 基础文件名
            base_name = FileUtils.get_file_stem(file_path)
            output_files = []

            # 执行拆分逻辑
            self._emit_progress(30, 100, "开始拆分...")

            # 输出时间周期设置信息
            if time_period:
                period_desc = TIME_PERIOD_DESCRIPTIONS.get(time_period, time_period)
                print(f"  时间周期: {period_desc} ({time_period})")
            else:
                print("  时间周期: 未设置（日期字段将按唯一值拆分）")

            if len(non_date_fields) >= 2:
                # 多个非日期字段：级联拆分
                print(f"\n  拆分策略: 级联拆分 {len(non_date_fields)} 个字段: {non_date_fields}")
                if date_fields and time_period:
                    # 有时间周期设置时，添加日期字段拆分
                    print(f"  附加时间字段: '{date_fields[0]}' ({TIME_PERIOD_DESCRIPTIONS.get(time_period, time_period)})")
                    output_files = self._split_multi_fields_with_date(
                        df, base_name, non_date_fields, date_fields[0], time_period
                    )
                elif date_fields and not time_period:
                    # 无时间周期设置时，将日期字段当作普通字段级联拆分
                    all_fields = non_date_fields + date_fields
                    print(f"  附加字段: {date_fields}（按唯一值拆分）")
                    output_files = self._split_multi_non_date_fields(
                        df, base_name, all_fields
                    )
                else:
                    output_files = self._split_multi_non_date_fields(
                        df, base_name, non_date_fields
                    )

            elif non_date_fields and date_fields:
                # 1个非日期字段 + 1个日期字段
                if time_period:
                    # 有时间周期设置：组合拆分
                    print(f"\n  拆分策略: 按 '{non_date_fields[0]}' + '{date_fields[0]}' ({TIME_PERIOD_DESCRIPTIONS.get(time_period, time_period)})")
                    output_files = self._split_by_non_date_and_date(
                        df, base_name, non_date_fields[0], date_fields[0], time_period
                    )
                else:
                    # 无时间周期设置：级联按唯一值拆分
                    print(f"\n  拆分策略: 级联拆分 '{non_date_fields[0]}' + '{date_fields[0]}'（按唯一值）")
                    output_files = self._split_multi_non_date_fields(
                        df, base_name, [non_date_fields[0], date_fields[0]]
                    )

            elif non_date_fields:
                # 仅按非日期字段拆分
                print(f"\n  拆分策略: 按 '{non_date_fields[0]}'")
                output_files = self._split_by_non_date(df, base_name, non_date_fields[0])

            elif date_fields:
                # 仅按日期字段拆分
                if time_period:
                    print(f"\n  拆分策略: 按 '{date_fields[0]}' ({TIME_PERIOD_DESCRIPTIONS.get(time_period, time_period)})")
                    output_files = self._split_by_date(df, base_name, date_fields[0], time_period)
                else:
                    # 无时间周期设置，按日期唯一值拆分
                    print(f"\n  拆分策略: 按 '{date_fields[0]}'（按唯一值）")
                    output_files = self._split_by_non_date(df, base_name, date_fields[0])

            # 输出结果统计
            self._emit_progress(90, 100, "完成拆分")
            # 确保统计正确：使用实际生成的文件列表长度
            actual_output_count = len(self.stats['output_file_list'])
            print(f"\n  ✅ 完成! 生成 {actual_output_count} 个文件:")
            for file_name, rows in output_files:
                print(f"     - {file_name} ({rows:,} 行)")

            self._emit_progress(100, 100, f"完成! 生成 {actual_output_count} 个文件")

        except Exception as e:
            error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
            print(f"  ❌ {error_msg}")
            self._emit_progress(100, 100, f"错误: {error_msg}")
            self.stats['errors'].append(error_msg)
            import traceback
            traceback.print_exc()

    def print_summary(self):
        """打印处理摘要"""
        print(f"\n{'=' * 60}")
        print("处理完成!")
        print(f"{'=' * 60}")
        print(f"输入文件: {self.stats['total_files']}")
        print(f"总行数: {self.stats['total_rows']:,}")
        print(f"输出文件: {self.stats['output_files']}")
        print(f"输出目录: {os.path.abspath(self.output_dir)}")

        if self.stats['errors']:
            print(f"\n⚠️  错误 ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"  - {error}")
