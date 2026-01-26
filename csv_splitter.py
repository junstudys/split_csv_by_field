#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 智能拆分工具 - 主入口文件
版本: v2.0

新功能：
- 支持更多日期格式: yyyy/MM/dd, yyyy/MM/dd HH:mm:ss
- 新增时间周期: 半年(H)、半月(HM)
- 模块化代码结构
- 改进的错误处理

使用示例：
    # 查看字段
    python csv_splitter.py list-fields --file data.csv

    # 按省份拆分
    python csv_splitter.py split --input data.csv --split-fields "省份"

    # 按省份和月份拆分
    python csv_splitter.py split --input data.csv --split-fields "省份,订单日期" --time-period M

    # 按季度拆分，大文件二次拆分
    python csv_splitter.py split --input data.csv --split-fields "订单日期" --time-period Q --max-rows 100000

    # 按半月拆分
    python csv_splitter.py split --input data.csv --split-fields "订单日期" --time-period HM

    # 批量处理文件夹
    python csv_splitter.py split --input ./data/ --split-fields "订单日期" --time-period Q --recursive
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from src.cli import main

if __name__ == '__main__':
    main()
