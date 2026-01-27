"""
预览确认页面
显示配置摘要并确认执行
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QTextEdit
)

from .base_page import BasePage
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # noqa: E402
from src.utils.constants import TIME_PERIODS, TIME_PERIOD_DESCRIPTIONS  # noqa: E402
from src.utils.file_utils import FileUtils  # noqa: E402


class PreviewPage(BasePage):
    """预览确认页面"""

    PAGE_NAME = 'preview'
    PAGE_TITLE = '预览确认'

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.config_summary = {}

    def _create_content(self):
        """创建页面内容"""
        # 说明区域
        info_section = self._create_section(
            '确认配置',
            '请仔细检查以下配置，确认无误后点击"开始拆分"按钮'
        )
        self.content_layout.addWidget(info_section)

        # 配置摘要卡片
        config_card = self._create_config_summary()
        self.content_layout.addWidget(config_card)

        # 添加弹性空间
        self.content_layout.addStretch(1)

        # 拆分策略说明
        strategy_card = self._create_strategy_info()
        self.content_layout.addWidget(strategy_card)

    def _create_config_summary(self):
        """创建配置摘要"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(10)

        # 输入文件
        self.file_info_label = QLabel()
        self.file_info_label.setWordWrap(True)
        card_layout.addWidget(self._create_info_row('输入文件:', self.file_info_label))

        # 文件大小和行数
        self.file_stats_label = QLabel()
        self.file_stats_label.setWordWrap(True)
        card_layout.addWidget(self._create_info_row('文件信息:', self.file_stats_label))

        # 拆分类型
        self.split_type_label = QLabel()
        self.split_type_label.setWordWrap(True)
        card_layout.addWidget(self._create_info_row('拆分类型:', self.split_type_label))

        # 拆分字段（仅按字段拆分时显示）
        self.fields_info_label = QLabel()
        self.fields_info_label.setWordWrap(True)
        card_layout.addWidget(self._create_info_row('拆分字段:', self.fields_info_label))

        # 时间周期（仅按字段拆分+有日期字段时显示）
        self.period_info_label = QLabel()
        self.period_info_label.setWordWrap(True)
        card_layout.addWidget(self._create_info_row('时间周期:', self.period_info_label))

        # 行数限制
        self.size_info_label = QLabel()
        self.size_info_label.setWordWrap(True)
        card_layout.addWidget(self._create_info_row('行数限制:', self.size_info_label))

        # 输出目录
        self.output_info_label = QLabel()
        self.output_info_label.setWordWrap(True)
        card_layout.addWidget(self._create_info_row('输出目录:', self.output_info_label))

        # 文件编码
        self.encoding_info_label = QLabel()
        card_layout.addWidget(self._create_info_row('文件编码:', self.encoding_info_label))

        return self._create_card('配置摘要', card_content)

    def _create_info_row(self, title, value_widget):
        """创建信息行"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setMinimumWidth(100)
        title_label.setStyleSheet('font-weight: bold; color: #2c3e50;')
        layout.addWidget(title_label)

        layout.addWidget(value_widget, 1)

        return widget

    def _create_strategy_info(self):
        """创建策略说明"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)

        self.strategy_text = QTextEdit()
        self.strategy_text.setReadOnly(True)
        self.strategy_text.setMaximumHeight(150)
        self.strategy_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        card_layout.addWidget(self.strategy_text)

        return self._create_card('拆分策略', card_content)

    def _create_buttons(self):
        """创建按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        back_btn = QPushButton('返回修改')
        back_btn.setMinimumWidth(120)
        back_btn.setMinimumHeight(45)
        back_btn.clicked.connect(self._on_back_clicked)
        button_layout.addWidget(back_btn)

        start_btn = QPushButton('开始拆分')
        start_btn.setMinimumWidth(140)
        start_btn.setMinimumHeight(45)
        start_btn.setObjectName('primaryButton')
        start_btn.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background-color: #229954;
            }
            QPushButton#primaryButton:pressed {
                background-color: #1e8449;
            }
        """)
        start_btn.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(start_btn)

        self.button_layout.addLayout(button_layout)

    def on_activated(self):
        """页面激活时调用"""
        self._load_config()

    def _load_config(self):
        """加载配置信息"""
        # 获取配置
        split_type = self.app.get_state('split_type', 'field')
        file_path = self.app.get_state('file_path', '')
        fields = self.app.get_state('fields', [])
        date_fields = self.app.get_state('date_fields', [])
        time_period = self.app.get_state('time_period')
        max_rows = self.app.get_state('max_rows')
        output_dir = self.app.get_state('output_dir', './split_data')
        is_folder = self.app.get_state('is_folder', False)
        recursive = self.app.get_state('recursive', False)

        # 文件信息
        if is_folder:
            self.file_info_label.setText(f'{file_path} (文件夹' + (' - 递归' if recursive else '') + ')')
        else:
            self.file_info_label.setText(file_path)

        # 文件统计（获取文件大小和行数）
        try:
            file_size = FileUtils.format_file_size(Path(file_path).stat().st_size)
            df = FileUtils.read_csv_with_encoding(file_path, encoding='auto', nrows=0)
            total_rows = len(df)
            self.file_stats_label.setText(f'大小: {file_size} | 总行数: {total_rows:,}')
        except Exception:
            self.file_stats_label.setText('无法获取文件信息')

        # 拆分类型
        if split_type == 'rows':
            self.split_type_label.setText('按行数拆分')
        else:
            self.split_type_label.setText('按字段拆分')

        # 拆分字段（仅按字段拆分时显示）
        if split_type == 'field' and fields:
            self.fields_info_label.setText(', '.join(fields))
            self.fields_info_label.parent().setVisible(True)
        else:
            self.fields_info_label.setText('-')
            self.fields_info_label.parent().setVisible(False)

        # 时间周期（仅按字段拆分+有日期字段时显示）
        if split_type == 'field' and date_fields and time_period:
            period_name = TIME_PERIODS.get(time_period, time_period)
            self.period_info_label.setText(f'{period_name} ({time_period})')
            self.period_info_label.parent().setVisible(True)
        else:
            self.period_info_label.setText('-')
            self.period_info_label.parent().setVisible(False)

        # 行数限制
        if max_rows:
            self.size_info_label.setText(f'每 {max_rows:,} 行')
        else:
            self.size_info_label.setText('不限制')

        # 输出目录
        self.output_info_label.setText(str(Path(output_dir).absolute()))

        # 编码（显示为自动检测）
        self.encoding_info_label.setText('自动检测')

        # 生成策略说明
        self._generate_strategy_description()

    def _generate_strategy_description(self):
        """生成策略说明"""
        split_type = self.app.get_state('split_type', 'field')
        fields = self.app.get_state('fields', [])
        date_fields = self.app.get_state('date_fields', [])
        time_period = self.app.get_state('time_period')
        max_rows = self.app.get_state('max_rows')

        strategy = []

        if split_type == 'rows':
            # 按行数拆分
            if max_rows:
                strategy.append(f"• 按行数拆分，每 {max_rows:,} 行一个文件")
            else:
                strategy.append("• 按行数拆分")
        else:
            # 按字段拆分
            if len(fields) == 1:
                strategy.append(f"• 按「{fields[0]}」字段拆分")
            elif len(fields) >= 2:
                strategy.append(f"• 级联拆分：{' → '.join(fields)}")

            # 时间周期
            if date_fields and time_period:
                period_name = TIME_PERIOD_DESCRIPTIONS.get(time_period, time_period)
                strategy.append(f"• 按「{date_fields[0]}」的{period_name}拆分")

            # 行数限制
            if max_rows:
                strategy.append(f"• 每个文件最多 {max_rows:,} 行")

        if not strategy:
            strategy.append("• 当前没有配置拆分策略")

        self.strategy_text.setText('\n'.join(strategy))

    def _on_start_clicked(self):
        """开始拆分按钮点击"""
        # 准备输出目录
        output_dir = self.app.get_state('output_dir', './split_data')

        # 确保目录存在
        FileUtils.ensure_output_dir(output_dir)

        # 发送开始信号
        self.app.signals.split_started.emit()

    def validate(self):
        """验证页面输入"""
        return True, ''

    def collect_data(self):
        """收集页面数据"""
        return self.app.state.copy()

    def get_prev_page(self):
        """获取上一页"""
        return self.main_window.PAGE_SPLIT
