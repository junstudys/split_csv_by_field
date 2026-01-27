"""
测试只按行数拆分的 CLI 功能
"""

import sys
from pathlib import Path
import tempfile
import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli import CLI


def create_test_csv(file_path, rows=1000):
    """创建测试 CSV 文件"""
    data = {
        'id': range(1, rows + 1),
        'name': [f'Item_{i}' for i in range(1, rows + 1)],
        'value': [i * 10 for i in range(1, rows + 1)],
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"✅ 创建测试文件: {file_path} ({rows} 行)")


def test_split_by_rows_only():
    """测试只按行数拆分"""
    print("\n" + "=" * 60)
    print("测试只按行数拆分功能")
    print("=" * 60)

    # 创建临时文件
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件
        test_file = Path(tmpdir) / 'test_data.csv'
        create_test_csv(test_file, rows=1000)

        # 创建输出目录
        output_dir = Path(tmpdir) / 'output'
        output_dir.mkdir()

        # 测试 CLI
        cli = CLI()

        print("\n📝 测试1: 只按行数拆分（500行/文件）")
        print("-" * 60)
        cli.split(
            input=str(test_file),
            split_fields=None,  # 不指定字段 = 只按行数拆分
            max_rows=500,
            output=str(output_dir),
            recursive=False,
            encoding='utf-8'
        )

        # 检查输出文件
        output_files = list(output_dir.glob('*.csv'))
        print(f"\n📊 生成文件: {len(output_files)} 个")
        for f in sorted(output_files):
            row_count = len(pd.read_csv(f))
            print(f"  - {f.name} ({row_count} 行)")

        # 验证
        assert len(output_files) == 2, f"预期2个文件，实际{len(output_files)}个"
        print("\n✅ 测试通过!")


def test_split_by_fields():
    """测试按字段拆分（确保原有功能正常）"""
    print("\n" + "=" * 60)
    print("测试按字段拆分功能（验证原有功能）")
    print("=" * 60)

    # 创建临时文件
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件
        test_file = Path(tmpdir) / 'test_data.csv'
        data = {
            'province': ['广东'] * 300 + ['浙江'] * 300 + ['江苏'] * 400,
            'city': ['深圳'] * 150 + ['广州'] * 150 + ['杭州'] * 300 + ['南京'] * 400,
            'value': range(1000),
        }
        df = pd.DataFrame(data)
        df.to_csv(test_file, index=False, encoding='utf-8')
        print(f"✅ 创建测试文件: {test_file} (1000 行)")

        # 创建输出目录
        output_dir = Path(tmpdir) / 'output'
        output_dir.mkdir()

        # 测试 CLI
        cli = CLI()

        print("\n📝 测试2: 按省份拆分")
        print("-" * 60)
        cli.split(
            input=str(test_file),
            split_fields='province',  # 按省份拆分
            max_rows=None,
            output=str(output_dir),
            recursive=False,
            encoding='utf-8'
        )

        # 检查输出文件
        output_files = list(output_dir.glob('*.csv'))
        print(f"\n📊 生成文件: {len(output_files)} 个")
        for f in sorted(output_files):
            row_count = len(pd.read_csv(f))
            print(f"  - {f.name} ({row_count} 行)")

        # 验证
        assert len(output_files) == 3, f"预期3个文件，实际{len(output_files)}个"
        print("\n✅ 测试通过!")


def test_split_by_fields_with_rows():
    """测试按字段拆分 + 行数限制"""
    print("\n" + "=" * 60)
    print("测试按字段拆分 + 行数限制")
    print("=" * 60)

    # 创建临时文件
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件
        test_file = Path(tmpdir) / 'test_data.csv'
        data = {
            'province': ['广东'] * 600 + ['浙江'] * 400,
            'value': range(1000),
        }
        df = pd.DataFrame(data)
        df.to_csv(test_file, index=False, encoding='utf-8')
        print(f"✅ 创建测试文件: {test_file} (1000 行)")

        # 创建输出目录
        output_dir = Path(tmpdir) / 'output'
        output_dir.mkdir()

        # 测试 CLI
        cli = CLI()

        print("\n📝 测试3: 按省份拆分 + 每文件最多400行")
        print("-" * 60)
        cli.split(
            input=str(test_file),
            split_fields='province',  # 按省份拆分
            max_rows=400,  # 二次按行数拆分
            output=str(output_dir),
            recursive=False,
            encoding='utf-8'
        )

        # 检查输出文件
        output_files = list(output_dir.glob('*.csv'))
        print(f"\n📊 生成文件: {len(output_files)} 个")
        for f in sorted(output_files):
            row_count = len(pd.read_csv(f))
            print(f"  - {f.name} ({row_count} 行)")

        # 验证：广东600行 -> 2个文件，浙江400行 -> 1个文件
        assert len(output_files) == 3, f"预期3个文件，实际{len(output_files)}个"
        print("\n✅ 测试通过!")


if __name__ == '__main__':
    print("\n🚀 开始 CLI 功能测试")

    try:
        test_split_by_rows_only()
        test_split_by_fields()
        test_split_by_fields_with_rows()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
