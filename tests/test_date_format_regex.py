"""
测试日期格式正则表达式
"""

import sys
from pathlib import Path
import re

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.constants import DATE_FORMATS  # noqa: E402


def test_date_format_patterns():
    """测试日期格式识别"""

    print("=" * 60)
    print("测试日期格式正则表达式")
    print("=" * 60)

    # 测试用例：(value, expected_format, should_match)
    test_cases = [
        # yyyyMM 格式
        ("202401", "yyyyMM", True),
        ("202501", "yyyyMM", True),
        ("190001", "yyyyMM", True),  # 边界：1900年
        ("299912", "yyyyMM", True),  # 边界：2999年
        ("300001", "yyyyMM", True),  # 边界：3000年
        ("189912", "yyyyMM", False),  # 无效：年份 < 1900
        ("310001", "yyyyMM", False),  # 无效：年份 > 3000
        ("202400", "yyyyMM", False),  # 无效：月份 = 00
        ("202413", "yyyyMM", False),  # 无效：月份 > 12
        ("20240", "yyyyMM", False),   # 无效：长度不足

        # yyyy-MM 格式
        ("2024-01", "yyyy-MM", True),
        ("2024-12", "yyyy-MM", True),
        ("1900-01", "yyyy-MM", True),  # 边界
        ("2999-12", "yyyy-MM", True),  # 边界
        ("3000-01", "yyyy-MM", True),  # 边界：3000年
        ("1899-12", "yyyy-MM", False),  # 无效
        ("3100-01", "yyyy-MM", False),  # 无效
        ("2024-00", "yyyy-MM", False),  # 无效：月份 = 00
        ("2024-13", "yyyy-MM", False),  # 无效：月份 > 12

        # yyyyMMdd 格式
        ("20240115", "yyyyMMdd", True),
        ("19000101", "yyyyMMdd", True),  # 边界
        ("30001231", "yyyyMMdd", True),  # 边界

        # yyyy-MM-dd 格式
        ("2024-01-15", "yyyy-MM-dd", True),
        ("1900-01-01", "yyyy-MM-dd", True),  # 边界
        ("3000-12-31", "yyyy-MM-dd", True),  # 边界
    ]

    passed = 0
    failed = 0

    for value, expected_format, should_match in test_cases:
        pattern = DATE_FORMATS.get(expected_format)
        if pattern is None:
            print(f"❌ 格式 '{expected_format}' 不存在")
            failed += 1
            continue

        match = re.match(pattern, value)
        is_match = match is not None

        if is_match == should_match:
            status = "✓"
            passed += 1
        else:
            status = "❌"
            failed += 1

        match_result = "匹配" if is_match else "不匹配"
        expected = "应该匹配" if should_match else "不应该匹配"

        print(f"{status} '{value}' -> '{expected_format}': {match_result} ({expected})")

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


def test_year_edge_cases():
    """测试年份边界情况"""

    print("\n" + "=" * 60)
    print("测试年份边界情况")
    print("=" * 60)

    # yyyyMM 格式测试
    pattern = DATE_FORMATS['yyyyMM']

    edge_cases = [
        # (year, should_match)
        ("189912", False),  # 1899: < 1900
        ("190001", True),   # 1900: = 1900
        ("190012", True),   # 1900: = 1900
        ("195001", True),   # 1950: 中间值
        ("199912", True),   # 1999: 19xx最大值
        ("200001", True),   # 2000: 20xx最小值
        ("202401", True),   # 2024: 当前年份
        ("299912", True),   # 2999: 29xx最大值
        ("300001", True),   # 3000: = 3000
        ("300012", True),   # 3000: = 3000
        ("310001", False),  # 3100: > 3000
    ]

    passed = 0
    failed = 0

    for value, should_match in edge_cases:
        match = re.match(pattern, value)
        is_match = match is not None

        if is_match == should_match:
            status = "✓"
            passed += 1
        else:
            status = "❌"
            failed += 1

        match_result = "匹配" if is_match else "不匹配"
        expected = "应该匹配" if should_match else "不应该匹配"

        print(f"{status} 年份 {value[:4]}: {match_result} ({expected})")

    print("\n" + "=" * 60)
    print(f"边界测试: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


def test_month_validation():
    """测试月份验证"""

    print("\n" + "=" * 60)
    print("测试月份验证")
    print("=" * 60)

    # yyyyMM 格式测试
    pattern = DATE_FORMATS['yyyyMM']

    month_cases = [
        # (value, should_match, description)
        ("202400", False, "月份 00"),
        ("202401", True, "月份 01"),
        ("202409", True, "月份 09"),
        ("202410", True, "月份 10"),
        ("202411", True, "月份 11"),
        ("202412", True, "月份 12"),
        ("202413", False, "月份 13"),
    ]

    passed = 0
    failed = 0

    for value, should_match, description in month_cases:
        match = re.match(pattern, value)
        is_match = match is not None

        if is_match == should_match:
            status = "✓"
            passed += 1
        else:
            status = "❌"
            failed += 1

        match_result = "匹配" if is_match else "不匹配"
        expected = "应该匹配" if should_match else "不应该匹配"

        print(f"{status} {description}: '{value}' {match_result} ({expected})")

    print("\n" + "=" * 60)
    print(f"月份测试: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    all_passed = True

    all_passed = test_date_format_patterns() and all_passed
    all_passed = test_year_edge_cases() and all_passed
    all_passed = test_month_validation() and all_passed

    if all_passed:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 部分测试失败!")
