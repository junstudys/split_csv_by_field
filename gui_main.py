#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 智能拆分工具 - GUI 入口文件
版本: v2.1.0

使用方法：
    python gui_main.py

或：
    python -m gui_main
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication
from src.gui.core.app import CSVSplitterApp


def main():
    """主入口"""
    # 创建应用程序
    app = CSVSplitterApp(sys.argv)

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
