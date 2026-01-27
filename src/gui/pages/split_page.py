"""
拆分设置页面
配置时间周期和行数限制
支持三种模式的动态显示
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QWidget, QRadioButton,
    QLineEdit, QFileDialog, QGridLayout
)

from .base_page import BasePage
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # noqa: E402
from src.utils.constants import TIME_PERIODS, TIME_PERIOD_DESCRIPTIONS  # noqa: E402


class SplitPage(BasePage):
    """拆分设置页面"""

    PAGE_NAME = 'split'
    PAGE_TITLE = '拆分设置'

    def _create_content(self):
        """创建页面内容"""
        # 说明区域
        info_section = self._create_section(
            '配置拆分选项',
            '设置时间周期（如有日期字段）和单文件最大行数限制'
        )
        self.content_layout.addWidget(info_section)

        # 设置卡片容器 - 动态内容区域
        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.settings_layout.setSpacing(20)
        self.content_layout.addWidget(self.settings_container)

        # 添加弹性空间
        self.content_layout.addStretch(1)

        # 创建输出目录卡片（所有模式都需要）
        output_card = self._create_output_dir()
        self.content_layout.addWidget(output_card)

    def _setup_rows_only_mode(self):
        """设置按行数拆分模式"""
        # 清空现有内容
        self._clear_settings_layout()

        # 创建行数拆分卡片
        rows_card = self._create_rows_only_card()
        self.settings_layout.addWidget(rows_card)

    def _setup_field_without_date_mode(self):
        """设置按字段拆分 + 无日期字段模式"""
        # 清空现有内容
        self._clear_settings_layout()

        # 创建行数限制卡片（简化版）
        size_card = self._create_size_limit_simple()
        self.settings_layout.addWidget(size_card)

    def _setup_field_with_date_mode(self):
        """设置按字段拆分 + 有日期字段模式"""
        # 清空现有内容
        self._clear_settings_layout()

        # 使用两列布局
        grid_container = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # 时间周期卡片
        time_card = self._create_time_period()
        grid_layout.addWidget(time_card, 0, 0)

        # 行数限制卡片
        size_card = self._create_size_limit()
        grid_layout.addWidget(size_card, 0, 1)

        grid_container.setLayout(grid_layout)
        self.settings_layout.addWidget(grid_container)

    def _clear_settings_layout(self):
        """清空设置布局"""
        while self.settings_layout.count():
            child = self.settings_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _create_rows_only_card(self):
        """创建按行数拆分卡片"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(12)

        # 标题
        title_label = QLabel('行数拆分设置')
        title_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        card_layout.addWidget(title_label)

        # 行数输入
        size_label = QLabel('单文件最大行数:')
        size_label.setStyleSheet('font-weight: bold; margin-top: 5px;')
        card_layout.addWidget(size_label)

        self.rows_max_rows_spin = QSpinBox()
        self.rows_max_rows_spin.setRange(1, 10000000)
        self.rows_max_rows_spin.setValue(500000)
        self.rows_max_rows_spin.setSuffix(' 行')
        self.rows_max_rows_spin.setMinimumHeight(35)
        card_layout.addWidget(self.rows_max_rows_spin)

        # 说明
        info_text = """
        <div style="color: #7f8c8d; font-size: 12px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;">
        <b>说明：</b><br>
        • 大文件将被拆分成多个小文件<br>
        • 每个文件最多包含指定行数<br>
        • 文件命名：原文件名_part1.csv、原文件名_part2.csv...
        </div>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        card_layout.addWidget(info_label)

        return self._create_card('按行数拆分', card_content)

    def _create_time_period(self):
        """创建时间周期设置"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(12)

        # 是否启用时间周期拆分
        self.enable_time_checkbox = QRadioButton('按时间周期拆分（需要选择日期字段）')
        self.enable_time_checkbox.setChecked(True)
        self.enable_time_checkbox.toggled.connect(self._on_time_toggled)
        card_layout.addWidget(self.enable_time_checkbox)

        # 时间周期选择
        period_label = QLabel('时间周期:')
        period_label.setStyleSheet('font-weight: bold; margin-top: 5px;')
        card_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.setMinimumHeight(35)
        for code, name in TIME_PERIODS.items():
            self.period_combo.addItem(f'{name} ({code})', code)
        self.period_combo.setCurrentIndex(0)  # 默认选择年（索引 0）
        card_layout.addWidget(self.period_combo)

        self.period_desc_label = QLabel('')
        self.period_desc_label.setStyleSheet('color: #7f8c8d; padding: 8px; background-color: #f8f9fa; border-radius: 4px;')
        self.period_desc_label.setWordWrap(True)
        card_layout.addWidget(self.period_desc_label)

        # 更新描述
        self._update_period_description()
        self.period_combo.currentIndexChanged.connect(self._update_period_description)

        return self._create_card('时间周期设置', card_content)

    def _create_size_limit(self):
        """创建行数限制设置（完整版，带可选开关）"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(12)

        # 是否启用行数限制
        self.enable_size_checkbox = QRadioButton('按行数拆分大文件')
        self.enable_size_checkbox.setChecked(False)
        self.enable_size_checkbox.toggled.connect(self._on_size_toggled)
        card_layout.addWidget(self.enable_size_checkbox)

        # 行数输入
        size_label = QLabel('单文件最大行数:')
        size_label.setStyleSheet('font-weight: bold; margin-top: 5px;')
        card_layout.addWidget(size_label)

        self.max_rows_spin = QSpinBox()
        self.max_rows_spin.setRange(1, 10000000)
        self.max_rows_spin.setValue(500000)
        self.max_rows_spin.setSuffix(' 行')
        self.max_rows_spin.setMinimumHeight(35)
        self.max_rows_spin.setEnabled(False)
        card_layout.addWidget(self.max_rows_spin)

        # 说明
        info_label = QLabel('💡 注意：行数拆分会在字段拆分的基础上进行二次拆分')
        info_label.setStyleSheet('color: #f39c12; font-size: 12px; padding: 8px; background-color: #fef9e7; border-radius: 4px;')
        info_label.setWordWrap(True)
        card_layout.addWidget(info_label)

        return self._create_card('行数限制设置', card_content)

    def _create_size_limit_simple(self):
        """创建行数限制设置（简化版，用于按字段拆分+无日期字段）"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(12)

        # 标题
        title_label = QLabel('行数限制设置')
        title_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        card_layout.addWidget(title_label)

        # 两个选项
        self.simple_no_limit_radio = QRadioButton('不进行行数拆分（保持完整）')
        self.simple_no_limit_radio.setChecked(True)
        self.simple_no_limit_radio.toggled.connect(self._on_simple_limit_toggled)
        card_layout.addWidget(self.simple_no_limit_radio)

        self.simple_limit_radio = QRadioButton('按行数拆分大文件')
        self.simple_limit_radio.toggled.connect(self._on_simple_limit_toggled)
        card_layout.addWidget(self.simple_limit_radio)

        # 行数输入
        size_label = QLabel('单文件最大行数:')
        size_label.setStyleSheet('font-weight: bold; margin-top: 5px;')
        card_layout.addWidget(size_label)

        self.simple_max_rows_spin = QSpinBox()
        self.simple_max_rows_spin.setRange(1, 10000000)
        self.simple_max_rows_spin.setValue(500000)
        self.simple_max_rows_spin.setSuffix(' 行')
        self.simple_max_rows_spin.setMinimumHeight(35)
        self.simple_max_rows_spin.setEnabled(False)
        card_layout.addWidget(self.simple_max_rows_spin)

        # 说明
        info_text = """
        <div style="color: #7f8c8d; font-size: 12px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;">
        <b>💡 说明：</b>选择的字段不包含日期类型，文件将按字段唯一值拆分。<br>
        可选择是否对拆分后的文件进行行数限制。
        </div>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        card_layout.addWidget(info_label)

        return self._create_card('', card_content)

    def _create_output_dir(self):
        """创建输出目录设置"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(12)

        # 标签
        dir_label = QLabel('输出目录:')
        dir_label.setStyleSheet('font-weight: bold;')
        card_layout.addWidget(dir_label)

        # 路径输入和浏览按钮
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(10)

        self.output_dir_input = QLineEdit()
        self.output_dir_input.setText('./split_data')
        self.output_dir_input.setPlaceholderText('选择输出目录...')
        self.output_dir_input.setMinimumHeight(35)
        dir_layout.addWidget(self.output_dir_input)

        browse_btn = QPushButton('浏览...')
        browse_btn.setMinimumWidth(100)
        browse_btn.setMinimumHeight(35)
        browse_btn.clicked.connect(self._on_browse_output)
        dir_layout.addWidget(browse_btn)

        card_layout.addLayout(dir_layout)

        # 说明
        info_label = QLabel('📁 拆分后的文件将保存到指定目录')
        info_label.setStyleSheet('color: #7f8c8d; font-size: 12px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;')
        card_layout.addWidget(info_label)

        return self._create_card('输出设置', card_content)

    def _create_buttons(self):
        """创建按钮"""
        self._create_nav_buttons(show_back=True, show_next=True)

    def _on_time_toggled(self, checked):
        """时间周期切换"""
        self.period_combo.setEnabled(checked)

    def _on_size_toggled(self, checked):
        """行数限制切换"""
        self.max_rows_spin.setEnabled(checked)

    def _on_simple_limit_toggled(self):
        """简化版行数限制切换"""
        self.simple_max_rows_spin.setEnabled(self.simple_limit_radio.isChecked())

    def _update_period_description(self):
        """更新时间周期描述"""
        code = self.period_combo.currentData()
        desc = TIME_PERIOD_DESCRIPTIONS.get(code, '')
        self.period_desc_label.setText(desc)

    def _on_browse_output(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            '选择输出目录',
            str(Path.cwd())
        )
        if dir_path:
            self.output_dir_input.setText(dir_path)

    def on_activated(self):
        """页面激活时调用"""
        split_type = self.app.get_state('split_type', 'field')

        if split_type == 'rows':
            # 按行数拆分模式
            self._setup_rows_only_mode()
            self._restore_rows_only_data()
        else:
            # 按字段拆分模式
            # 检查用户选择的字段中是否包含日期字段
            selected_fields = self.app.get_state('fields', [])
            date_fields_in_file = self.app.get_state('date_fields', [])
            has_selected_date_field = any(f in date_fields_in_file for f in selected_fields)

            if has_selected_date_field:
                # 选择了日期字段：显示时间周期 + 行数限制
                self._setup_field_with_date_mode()
                self._restore_field_with_date_data()
            else:
                # 没有选择日期字段：只显示行数限制
                self._setup_field_without_date_mode()
                self._restore_field_without_date_data()

    def _restore_rows_only_data(self):
        """恢复按行数拆分模式的数据"""
        max_rows = self.app.get_state('max_rows')
        if max_rows is not None:
            self.rows_max_rows_spin.setValue(max_rows)
        else:
            # 如果没有设置过，使用默认值
            self.rows_max_rows_spin.setValue(500000)

        output_dir = self.app.get_state('output_dir')
        if output_dir:
            self.output_dir_input.setText(output_dir)

    def _restore_field_with_date_data(self):
        """恢复按字段拆分+有日期字段模式的数据"""
        time_period = self.app.get_state('time_period')
        if time_period is not None:
            for i in range(self.period_combo.count()):
                if self.period_combo.itemData(i) == time_period:
                    self.period_combo.setCurrentIndex(i)
                    break
            # 同时选中"按时间周期拆分"单选按钮
            self.enable_time_checkbox.setChecked(True)
        else:
            # 没有时间周期，取消选中
            self.enable_time_checkbox.setChecked(False)

        max_rows = self.app.get_state('max_rows')
        if max_rows is not None:
            # 有行数限制
            self.enable_size_checkbox.setChecked(True)
            self.max_rows_spin.setValue(max_rows)
            self.max_rows_spin.setEnabled(True)
        else:
            # 没有行数限制
            self.enable_size_checkbox.setChecked(False)
            self.max_rows_spin.setEnabled(False)

        output_dir = self.app.get_state('output_dir')
        if output_dir:
            self.output_dir_input.setText(output_dir)

    def _restore_field_without_date_data(self):
        """恢复按字段拆分+无日期字段模式的数据"""
        max_rows = self.app.get_state('max_rows')
        if max_rows is not None:
            # 有行数限制：选中"按行数拆分"单选按钮
            self.simple_limit_radio.setChecked(True)
            self.simple_max_rows_spin.setValue(max_rows)
            self.simple_max_rows_spin.setEnabled(True)
        else:
            # 没有行数限制：选中"不进行行数拆分"单选按钮
            self.simple_no_limit_radio.setChecked(True)
            self.simple_max_rows_spin.setEnabled(False)

        output_dir = self.app.get_state('output_dir')
        if output_dir:
            self.output_dir_input.setText(output_dir)

    def validate(self):
        """验证页面输入"""
        output_dir = self.output_dir_input.text()
        if not output_dir or not output_dir.strip():
            return False, '请设置输出目录'

        return True, ''

    def collect_data(self):
        """收集页面数据"""
        split_type = self.app.get_state('split_type', 'field')

        if split_type == 'rows':
            # 按行数拆分模式
            max_rows = self.rows_max_rows_spin.value()
            time_period = None
        else:
            # 按字段拆分模式 - 根据 UI 控件判断当前模式
            if hasattr(self, 'enable_time_checkbox'):
                # 选择了日期字段：有时间周期控件
                if self.enable_time_checkbox.isChecked():
                    time_period = self.period_combo.currentData()
                else:
                    time_period = None

                if self.enable_size_checkbox.isChecked():
                    max_rows = self.max_rows_spin.value()
                else:
                    max_rows = None
            elif hasattr(self, 'simple_limit_radio'):
                # 没选择日期字段：只有简化的行数限制控件
                if self.simple_limit_radio.isChecked():
                    max_rows = self.simple_max_rows_spin.value()
                else:
                    max_rows = None
                time_period = None
            else:
                # 默认情况
                max_rows = None
                time_period = None

        # 输出目录
        output_dir = self.output_dir_input.text().strip()

        # 保存状态
        self.app.set_state('time_period', time_period)
        self.app.set_state('max_rows', max_rows)
        self.app.set_state('output_dir', output_dir)

        return {
            'time_period': time_period,
            'max_rows': max_rows,
            'output_dir': output_dir,
        }

    def get_next_page(self):
        """获取下一页"""
        return self.main_window.PAGE_PREVIEW

    def get_prev_page(self):
        """获取上一页"""
        split_type = self.app.get_state('split_type', 'field')
        if split_type == 'rows':
            return self.main_window.PAGE_FILE
        else:
            return self.main_window.PAGE_FIELD
