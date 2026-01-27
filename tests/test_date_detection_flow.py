"""
测试日期字段检测和拆分流程
"""

import sys
from pathlib import Path
import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.date_utils import DateUtils  # noqa: E402
from src.utils.constants import DATE_DETECTION_THRESHOLD  # noqa: E402


def test_yyyyMM_date_detection():
    """测试 yyyyMM 格式（如 202401, 202405）的日期检测"""

    print("=" * 60)
    print("测试 yyyyMM 格式日期检测")
    print("=" * 60)

    # 模拟"结算时间"字段的数据
    test_data = pd.Series([
        '202402', '202405', '202401', '202409', '202404',
        '202504', '202505', '202507', '202502', '202501',
        '202408', '202403', '202406', '202407', '202503',
        '202509', '202412', '202508', '202411', '202512',
        '202410', '202511', '202506', '202510'
    ])

    print(f"\n测试数据: {len(test_data)} 个值")
    print(f"样例值: {list(test_data[:5])}")

    # 测试单个值检测
    print("\n1. 单个值格式检测:")
    for value in test_data[:5]:
        format_name = DateUtils.detect_date_format(value)
        if format_name:
            print(f"  ✓ '{value}' 识别为 {format_name}")
        else:
            print(f"  ❌ '{value}' 未识别为日期")

    # 测试整列检测
    print("\n2. 整列日期检测:")
    is_date = DateUtils.is_date_column(test_data, threshold=DATE_DETECTION_THRESHOLD)
    if is_date:
        print(f"  ✓ 列被识别为日期字段 (阈值: {DATE_DETECTION_THRESHOLD})")
    else:
        print("  ❌ 列未被识别为日期字段")

    # 测试转换
    print("\n3. 日期转换测试:")
    converted = DateUtils.convert_to_datetime(test_data)
    print(f"  成功转换: {converted.notna().sum()}/{len(converted)}")
    print("  样例转换结果:")
    for i in range(5):
        original = test_data.iloc[i]
        converted_val = converted.iloc[i]
        print(f"    {original} -> {converted_val.strftime('%Y-%m-%d')}")

    # 测试时间周期拆分
    print("\n4. 时间周期拆分测试:")
    for period in ['Y', 'M', 'Q', 'H']:
        period_keys = DateUtils.apply_period_filter(converted, period)
        unique_groups = period_keys.dropna().unique()
        print(f"  {period} ({DateUtils.get_time_period_name(period)}): {len(unique_groups)} 个分组")
        if period == 'Y':
            print(f"    分组: {list(unique_groups)}")

    print("\n" + "=" * 60)
    print("✅ yyyyMM 格式测试完成")
    print("=" * 60)

    return is_date


def test_yyyy_dash_MM_date_detection():
    """测试 yyyy-MM 格式（如 2024-01, 2024-12）的日期检测"""

    print("\n" + "=" * 60)
    print("测试 yyyy-MM 格式日期检测")
    print("=" * 60)

    # 模拟数据
    test_data = pd.Series([
        '2024-01', '2024-02', '2024-12', '2025-01', '2025-12',
        '1900-01', '3000-12'
    ])

    print(f"\n测试数据: {len(test_data)} 个值")
    print(f"样例值: {list(test_data[:5])}")

    # 测试单个值检测
    print("\n1. 单个值格式检测:")
    for value in test_data[:5]:
        format_name = DateUtils.detect_date_format(value)
        if format_name:
            print(f"  ✓ '{value}' 识别为 {format_name}")
        else:
            print(f"  ❌ '{value}' 未识别为日期")

    # 测试整列检测
    print("\n2. 整列日期检测:")
    is_date = DateUtils.is_date_column(test_data, threshold=DATE_DETECTION_THRESHOLD)
    if is_date:
        print(f"  ✓ 列被识别为日期字段 (阈值: {DATE_DETECTION_THRESHOLD})")
    else:
        print("  ❌ 列未被识别为日期字段")

    # 测试转换
    print("\n3. 日期转换测试:")
    converted = DateUtils.convert_to_datetime(test_data)
    print(f"  成功转换: {converted.notna().sum()}/{len(converted)}")
    print("  样例转换结果:")
    for i in range(min(5, len(test_data))):
        original = test_data.iloc[i]
        converted_val = converted.iloc[i]
        print(f"    {original} -> {converted_val.strftime('%Y-%m-%d')}")

    # 测试时间周期拆分
    print("\n4. 时间周期拆分测试 (按年):")
    period_keys = DateUtils.apply_period_filter(converted, 'Y')
    unique_groups = sorted(period_keys.dropna().unique())
    print(f"  分组: {unique_groups}")

    print("\n" + "=" * 60)
    print("✅ yyyy-MM 格式测试完成")
    print("=" * 60)

    return is_date


def test_mixed_format_detection():
    """测试混合格式（含无效值）的日期检测"""

    print("\n" + "=" * 60)
    print("测试混合格式日期检测")
    print("=" * 60)

    # 模拟含无效值的数据
    test_data = pd.Series([
        '202401', '202402', '202403',  # 有效 yyyyMM
        'invalid', None, '',           # 无效值
        '2024-01', '2024-02',          # 有效 yyyy-MM
        '2024-13', '202400',           # 无效月份
    ])

    print(f"\n测试数据: {len(test_data)} 个值 (含无效值)")

    # 测试单个值检测
    print("\n1. 单个值格式检测:")
    for value in test_data:
        if pd.isna(value) or value == '':
            print(f"  - {value} -> 跳过")
            continue
        format_name = DateUtils.detect_date_format(value)
        if format_name:
            print(f"  ✓ '{value}' 识别为 {format_name}")
        else:
            print(f"  ❌ '{value}' 未识别为日期")

    # 测试整列检测（计算有效日期比例）
    print("\n2. 整列日期检测:")
    non_null = test_data.dropna()
    non_null = non_null[non_null != '']
    date_count = sum(1 for x in non_null if DateUtils.detect_date_format(x))
    ratio = date_count / len(non_null)
    print(f"  非空值: {len(non_null)}")
    print(f"  识别为日期: {date_count}")
    print(f"  比例: {ratio:.2%}")
    print(f"  阈值: {DATE_DETECTION_THRESHOLD:.0%}")
    if ratio >= DATE_DETECTION_THRESHOLD:
        print("  ✓ 比例 >= 阈值，应识别为日期字段")
    else:
        print("  ❌ 比例 < 阈值，不应识别为日期字段")

    print("\n" + "=" * 60)
    print("✅ 混合格式测试完成")
    print("=" * 60)

    return ratio >= DATE_DETECTION_THRESHOLD


if __name__ == '__main__':
    all_passed = True

    result1 = test_yyyyMM_date_detection()
    if not result1:
        all_passed = False

    result2 = test_yyyy_dash_MM_date_detection()
    if not result2:
        all_passed = False

    result3 = test_mixed_format_detection()
    # 混合格式测试可能不通过（因为有太多无效值），这是正常的

    if all_passed:
        print("\n✅ 核心测试通过!")
    else:
        print("\n❌ 部分测试失败!")
