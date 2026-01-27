"""
命令行接口类
提供 split 和 list-fields 命令
"""

import fire
from .splitter import CSVSplitter
from .utils import DateUtils, FileUtils
from .utils.constants import (
    DEFAULT_MAX_ROWS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_ENCODING,
    TIME_PERIODS,
)


class CLI:
    """命令行接口类"""

    def split(self,
              input,
              split_fields=None,
              time_period=None,
              max_rows=None,
              output=DEFAULT_OUTPUT_DIR,
              recursive=False,
              encoding=DEFAULT_ENCODING):
        """
        拆分CSV文件

        Args:
            input: 输入文件或文件夹路径
            split_fields: 拆分字段，多个字段用逗号分隔（如: "省份,订单日期"）
                         None 表示只按行数拆分
            time_period: 时间周期 (Y=年, H=半年, Q=季度, M=月, HM=半月, D=日)
            max_rows: 单文件最大行数
                     - 按字段拆分模式: None=不拆分, 整数=二次拆分
                     - 按行数拆分模式: 必须设置，默认500000
            output: 输出目录
            recursive: 是否递归处理子文件夹
            encoding: 文件编码 (auto/utf-8/gbk等)

        Examples:
            # 只按行数拆分（默认50万行）
            python csv_splitter.py split --input data.csv --max-rows 500000

            # 只按行数拆分文件夹
            python csv_splitter.py split --input ./data/ --max-rows 500000

            # 按省份拆分
            python csv_splitter.py split --input data.csv --split-fields "省份"

            # 按省份和月份拆分
            python csv_splitter.py split --input data.csv --split-fields "省份,订单日期" --time-period M

            # 按季度拆分，大文件二次拆分
            python csv_splitter.py split --input data.csv --split-fields "订单日期" --time-period Q --max-rows 100000

            # 批量处理文件夹
            python csv_splitter.py split --input ./data/ --split-fields "订单日期" --recursive
        """
        self._print_header()

        # 判断拆分模式
        is_rows_only_mode = split_fields is None

        # 按行数拆分模式：必须设置 max_rows
        if is_rows_only_mode:
            actual_max_rows = self._parse_max_rows(max_rows) if max_rows is not None else DEFAULT_MAX_ROWS
            self._print_config_rows_only(input, actual_max_rows, output, recursive)
        else:
            # 按字段拆分模式
            actual_max_rows = self._parse_max_rows(max_rows)
            self._print_config(input, split_fields, time_period, actual_max_rows, output, recursive)

            # 验证时间周期（仅在指定了时间周期时才验证）
            if time_period and time_period.strip() and not DateUtils.validate_time_period(time_period):
                print(f"❌ 错误: 无效的时间周期 '{time_period}'")
                print(f"   支持的周期: {', '.join(TIME_PERIODS.keys())}")
                print(f"   {', '.join([f'{k}={v}' for k, v in TIME_PERIODS.items()])}")
                return

            # 解析字段
            fields = self._parse_fields(split_fields)
            print(f"解析后的字段: {fields}\n")

        # 获取文件列表
        csv_files = FileUtils.get_csv_files(input, recursive)

        if not csv_files:
            print(f"❌ 错误: 在 '{input}' 中未找到CSV文件")
            return

        print(f"找到 {len(csv_files)} 个CSV文件\n")

        # 初始化拆分器
        splitter = CSVSplitter(max_rows=actual_max_rows, output_dir=output, encoding=encoding)

        # 准备输出目录
        if not FileUtils.prepare_output_dir(output, ask_user=True):
            print("❌ 已取消操作")
            return

        # 处理每个文件
        if is_rows_only_mode:
            # 只按行数拆分模式
            for csv_file in csv_files:
                splitter.split_by_rows_only(csv_file)
        else:
            # 按字段拆分模式
            for csv_file in csv_files:
                splitter.split_single_file(csv_file, fields, time_period)

        # 打印摘要
        splitter.print_summary()

    def list_fields(self, file, encoding=DEFAULT_ENCODING):
        """
        列出CSV文件的所有字段

        Args:
            file: CSV文件路径
            encoding: 文件编码

        Examples:
            python csv_splitter.py list-fields --file data.csv
        """
        print("\n📋 文件字段列表")
        print(f"{'=' * 60}")
        print(f"文件: {file}")

        try:
            if encoding == 'auto':
                encoding = FileUtils.detect_encoding(file)
                print(f"编码: {encoding}")

            df = FileUtils.read_csv_with_encoding(file, encoding=encoding, nrows=1000)

            print(f"\n总字段数: {len(df.columns)}")
            print(f"{'=' * 60}")

            for i, col in enumerate(df.columns, 1):
                # 检测是否为日期字段
                is_date = DateUtils.is_date_column(df[col])
                col_type = "📅 日期" if is_date else "📝 普通"

                # 样例值
                sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else "N/A"

                print(f"  {i:2d}. {col_type} | {col:30s} | 样例: {sample}")

        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def _print_header(self):
        """打印标题"""
        print("\n🚀 CSV 智能拆分工具 v2.0")
        print(f"{'=' * 60}")

    def _print_config(self, input, split_fields, time_period, max_rows, output, recursive):
        """打印配置信息"""
        print(f"输入路径: {input}")
        print(f"拆分字段: {split_fields}")
        # 时间周期：空字符串或None表示不需要按时间周期拆分
        if time_period and time_period.strip():
            print(f"时间周期: {time_period} ({TIME_PERIODS.get(time_period, '未知')})")
        else:
            print("时间周期:   (不需要)")

        # 行数拆分策略
        if max_rows is None:
            print("行数拆分: ❌ 不拆分")
        elif max_rows is True or max_rows == '':
            print(f"行数拆分: ✅ 默认 {DEFAULT_MAX_ROWS:,} 行")
        else:
            print(f"行数拆分: ✅ 每 {int(max_rows):,} 行")

        print(f"输出目录: {output}")
        print(f"递归处理: {'是' if recursive else '否'}")
        print(f"{'=' * 60}")

    def _print_config_rows_only(self, input, max_rows, output, recursive):
        """打印只按行数拆分的配置信息"""
        print(f"输入路径: {input}")
        print("拆分模式: 按行数拆分")
        print(f"行数限制: ✅ 每 {max_rows:,} 行")
        print(f"输出目录: {output}")
        print(f"递归处理: {'是' if recursive else '否'}")
        print(f"{'=' * 60}")

    def _parse_max_rows(self, max_rows):
        """
        解析 max_rows 参数

        Args:
            max_rows: 原始参数值

        Returns:
            int or None: 解析后的值
        """
        if max_rows is None:
            return None
        elif max_rows is True:
            return DEFAULT_MAX_ROWS
        elif isinstance(max_rows, (int, float)):
            return int(max_rows)
        elif isinstance(max_rows, str):
            # 去除前后空白，处理空字符串或纯空格字符串
            max_rows = max_rows.strip()
            if max_rows == '':
                return DEFAULT_MAX_ROWS
            try:
                return int(max_rows)
            except ValueError:
                print(f"⚠️  警告: 无效的 max_rows 值 '{max_rows}'，将使用默认值 {DEFAULT_MAX_ROWS}")
                return DEFAULT_MAX_ROWS
        else:
            print(f"⚠️  警告: 无法解析 max_rows 类型 {type(max_rows)}，将使用默认值 {DEFAULT_MAX_ROWS}")
            return DEFAULT_MAX_ROWS

    def _parse_fields(self, split_fields):
        """
        解析字段参数

        Args:
            split_fields: 字段参数（字符串、元组或列表）

        Returns:
            list: 字段列表
        """
        if isinstance(split_fields, str):
            return [f.strip() for f in split_fields.split(',')]
        elif isinstance(split_fields, (tuple, list)):
            return [str(f).strip() for f in split_fields]
        else:
            return [str(split_fields).strip()]


def main():
    """主入口"""
    fire.Fire(CLI)


if __name__ == '__main__':
    main()
