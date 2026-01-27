"""
GUI 应用程序类
提供全局状态管理和信号系统
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont
from ..main_window import MainWindow


class AppSignals(QObject):
    """全局信号类"""

    # 文件相关信号
    file_selected = pyqtSignal(str)  # 文件路径

    # 字段相关信号
    fields_selected = pyqtSignal(list)  # 字段列表

    # 配置相关信号
    split_config_changed = pyqtSignal(dict)  # 拆分配置

    # 进度相关信号
    split_progress = pyqtSignal(int, int, str)  # (current, total, message)
    split_started = pyqtSignal()
    split_finished = pyqtSignal(dict)  # 结果统计
    split_failed = pyqtSignal(str)  # 错误消息
    split_cancelled = pyqtSignal()

    # 导航相关信号
    navigate_to = pyqtSignal(str)  # 页面名称
    navigate_next = pyqtSignal()
    navigate_back = pyqtSignal()


class CSVSplitterApp(QApplication):
    """CSV 拆分器 GUI 应用程序"""

    def __init__(self, argv):
        """
        初始化应用程序

        Args:
            argv: 命令行参数
        """
        super().__init__(argv)

        # 应用程序名称
        self.setApplicationName('CSV 智能拆分工具')
        self.setApplicationVersion('2.2.0')
        self.setOrganizationName('JunStudio')

        # 全局信号
        self.signals = AppSignals()

        # 应用状态
        self.state = {
            'file_path': None,
            'split_type': 'field',  # 拆分类型: 'field' 或 'rows'
            'fields': [],
            'date_fields': [],  # 日期字段列表
            'non_date_fields': [],  # 非日期字段列表
            'time_period': None,  # 默认 None，由用户选择决定
            'max_rows': 500000,  # 默认 50 万行
            'output_dir': './split_data',
            'preview_data': None,
        }

        # 创建主窗口
        self.main_window = MainWindow(self)
        self.main_window.show()

        # 应用样式
        self._setup_fonts()

    def _setup_fonts(self):
        """设置默认字体"""
        font = QFont()
        font.setFamily('Microsoft YaHei, SimHei, Arial')
        font.setPointSize(10)
        self.setFont(font)

    def set_state(self, key, value):
        """
        设置应用状态

        Args:
            key: 状态键
            value: 状态值
        """
        self.state[key] = value

    def get_state(self, key, default=None):
        """
        获取应用状态

        Args:
            key: 状态键
            default: 默认值

        Returns:
            状态值
        """
        return self.state.get(key, default)

    def reset_state(self):
        """重置应用状态"""
        self.state = {
            'file_path': None,
            'split_type': 'field',  # 拆分类型: 'field' 或 'rows'
            'fields': [],
            'date_fields': [],  # 日期字段列表
            'non_date_fields': [],  # 非日期字段列表
            'time_period': None,  # 默认 None，由用户选择决定
            'max_rows': 500000,  # 默认 50 万行
            'output_dir': './split_data',
            'preview_data': None,
        }

    def navigate_to(self, page_name):
        """
        导航到指定页面

        Args:
            page_name: 页面名称
        """
        self.signals.navigate_to.emit(page_name)

    def navigate_next(self):
        """导航到下一页"""
        self.signals.navigate_next.emit()

    def navigate_back(self):
        """导航到上一页"""
        self.signals.navigate_back.emit()
