"""
日期处理工具类
提供日期格式检测、日期转换、时间周期处理等功能
"""

import re
import pandas as pd
from ..utils.constants import (
    DATE_FORMATS,
    DATE_FORMAT_STRINGS,
    TIME_PERIODS,
    DATE_DETECTION_THRESHOLD,
)


class DateUtils:
    """日期处理工具类"""

    @staticmethod
    def detect_date_format(value):
        """
        检测单个值的日期格式

        支持的格式：
        - yyyyMMdd: 20240115
        - yyyy-MM-dd: 2024-01-15
        - yyyy/MM/dd: 2024/01/15
        - yyyyMMdd HH:mm:ss: 20240115 14:30:00
        - yyyy-MM-dd HH:mm:ss: 2024-01-15 14:30:00
        - yyyy/MM/dd HH:mm:ss: 2024/01/15 14:30:00

        Args:
            value: 要检测的值

        Returns:
            str or None: 匹配的日期格式名称，不匹配返回 None
        """
        value_str = str(value).strip()
        for format_name, pattern in DATE_FORMATS.items():
            if re.match(pattern, value_str):
                return format_name
        return None

    @staticmethod
    def is_date_column(series, threshold=DATE_DETECTION_THRESHOLD):
        """
        判断列是否为日期类型

        Args:
            series: pandas Series
            threshold: 至少多少比例的值符合日期格式 (默认: 0.8)

        Returns:
            bool: 是否为日期字段
        """
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return False

        date_count = sum(1 for x in non_null_series if DateUtils.detect_date_format(x))
        ratio = date_count / len(non_null_series)
        return ratio >= threshold

    @staticmethod
    def convert_to_datetime(series):
        """
        智能转换为 datetime 类型

        Args:
            series: pandas Series

        Returns:
            pandas Series: 转换后的 datetime Series
        """
        # 首先尝试按格式逐个解析（避免将数字误认为时间戳）
        for fmt in DATE_FORMAT_STRINGS:
            try:
                result = pd.to_datetime(series, format=fmt, errors='coerce')
                # 检查是否有成功解析的值
                if result.notna().sum() > 0:
                    # 检查是否全部值都解析成功
                    if result.notna().sum() == len(series):
                        return result
                    # 如果只解析了部分，记录一下
                    # 但仍然继续尝试其他格式
            except Exception:
                continue

        # 最后尝试 pandas 自动解析（作为后备）
        try:
            result = pd.to_datetime(series, errors='coerce')
            if result.notna().any():
                return result
        except Exception:
            pass

        # 全部失败，返回 NaT
        return pd.to_datetime(series, errors='coerce')

    @staticmethod
    def get_period_label(date, period_type):
        """
        获取时间周期标签

        Args:
            date: pandas Timestamp
            period_type: 时间周期类型 (Y/H/Q/M/HM/D)

        Returns:
            str: 时间周期标签
        """
        year = date.year
        month = date.month
        day = date.day

        if period_type == 'Y':
            return str(year)

        elif period_type == 'H':
            # 半年: H1 = 1-6月, H2 = 7-12月
            half = 'H1' if month <= 6 else 'H2'
            return f'{year}-{half}'

        elif period_type == 'Q':
            # 季度
            quarter = (month - 1) // 3 + 1
            return f'{year}-Q{quarter}'

        elif period_type == 'M':
            # 月
            return f'{year}-{month:02d}'

        elif period_type == 'HM':
            # 半月: HM1 = 1-15日, HM2 = 16-月末
            half = 'HM1' if day <= 15 else 'HM2'
            return f'{year}-{month:02d}-{half}'

        elif period_type == 'D':
            # 日
            return f'{year}-{month:02d}-{day:02d}'

        return str(date)

    @staticmethod
    def apply_period_filter(series, period_type):
        """
        应用时间周期过滤，返回周期分组键
        统一返回字符串格式的Series，确保groupby行为一致

        Args:
            series: datetime Series 或 DatetimeIndex
            period_type: 时间周期类型

        Returns:
            Series: 字符串格式的周期分组键 Series
        """
        # 转换为 Series（如果是 DatetimeIndex）
        if isinstance(series, pd.DatetimeIndex):
            series = pd.Series(series)

        # 确保series是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(series):
            series = pd.to_datetime(series, errors='coerce')

        if period_type == 'Y':
            # 年: 返回 "2024"
            return series.dt.strftime('%Y').astype(str)

        elif period_type == 'H':
            # 半年: H1 = 1-6月, H2 = 7-12月
            return series.apply(
                lambda x: f"{x.year}-H1" if x.month <= 6 else f"{x.year}-H2" if pd.notna(x) else None
            )

        elif period_type == 'Q':
            # 季度: 返回 "2024-Q1"
            quarter = (series.dt.month - 1) // 3 + 1
            return series.dt.year.astype(str) + '-Q' + quarter.astype(str)

        elif period_type == 'M':
            # 月: 返回 "2024-01"
            return series.dt.strftime('%Y-%m')

        elif period_type == 'HM':
            # 半月: HM1 = 1-15日, HM2 = 16-月末
            return series.apply(
                lambda x: f"{x.year}-{x.month:02d}-HM1" if x.day <= 15 else f"{x.year}-{x.month:02d}-HM2" if pd.notna(x) else None
            )

        elif period_type == 'D':
            # 日: 返回 "2024-01-15"
            return series.dt.strftime('%Y-%m-%d')

        # 默认返回原始series
        return series

    @staticmethod
    def validate_time_period(period_type):
        """
        验证时间周期类型是否有效

        Args:
            period_type: 时间周期类型

        Returns:
            bool: 是否有效
        """
        return period_type in TIME_PERIODS

    @staticmethod
    def get_time_period_name(period_type):
        """
        获取时间周期中文名称

        Args:
            period_type: 时间周期类型

        Returns:
            str: 中文名称
        """
        return TIME_PERIODS.get(period_type, period_type)
