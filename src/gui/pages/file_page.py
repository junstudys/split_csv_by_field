"""
文件选择页面
允许用户选择要拆分的 CSV 文件
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QGroupBox, QRadioButton,
    QButtonGroup
)

from .base_page import BasePage
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # noqa: E402
from src.utils.file_utils import FileUtils  # noqa: E402


class FilePage(BasePage):
    """文件选择页面"""

    PAGE_NAME = 'file'
    PAGE_TITLE = '选择文件'

    def _create_content(self):
        """创建页面内容"""
        # 说明区域
        info_section = self._create_section(
            '选择 CSV 文件',
            '选择要拆分的 CSV 文件，或选择文件夹批量处理多个文件'
        )
        self.content_layout.addWidget(info_section)

        # 文件选择卡片
        file_card = self._create_file_selection()
        self.content_layout.addWidget(file_card)

        # 拆分类型选择卡片
        split_type_card = self._create_split_type_selection()
        self.content_layout.addWidget(split_type_card)

        # 添加弹性空间
        self.content_layout.addStretch(1)

    def _create_file_selection(self):
        """创建文件选择区域"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(15)

        # 选择模式
        mode_group = QGroupBox('选择模式')
        mode_layout = QVBoxLayout()

        self.mode_button_group = QButtonGroup()
        self.single_file_radio = QRadioButton('单个文件')
        self.folder_radio = QRadioButton('文件夹（批量处理）')

        self.mode_button_group.addButton(self.single_file_radio, 0)
        self.mode_button_group.addButton(self.folder_radio, 1)

        self.single_file_radio.setChecked(True)
        self.single_file_radio.toggled.connect(self._on_mode_changed)

        mode_layout.addWidget(self.single_file_radio)
        mode_layout.addWidget(self.folder_radio)
        mode_group.setLayout(mode_layout)

        card_layout.addWidget(mode_group)

        # 文件路径输入
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText('选择 CSV 文件或文件夹...')
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)

        self.browse_btn = QPushButton('浏览...')
        self.browse_btn.setMinimumWidth(100)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        path_layout.addWidget(self.browse_btn)

        card_layout.addLayout(path_layout)

        # 递归选项（仅文件夹模式）
        self.recursive_checkbox = QRadioButton('递归处理子文件夹')
        self.recursive_checkbox.setVisible(False)
        self.recursive_checkbox.setChecked(False)
        card_layout.addWidget(self.recursive_checkbox)

        # 文件信息
        self.file_info_label = QLabel('')
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setStyleSheet('color: #7f8c8d;')
        card_layout.addWidget(self.file_info_label)

        return self._create_card('', card_content)

    def _create_split_type_selection(self):
        """创建拆分类型选择区域"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(10)

        # 拆分类型选择
        type_group = QGroupBox('拆分类型')
        type_layout = QVBoxLayout()

        self.split_type_button_group = QButtonGroup()

        # 按字段拆分选项
        self.field_split_radio = QRadioButton('按字段拆分')
        self.field_split_radio.setChecked(True)
        self.field_split_radio.setToolTip('根据字段内容拆分文件，支持时间周期拆分和级联拆分')
        type_layout.addWidget(self.field_split_radio)

        # 按字段拆分说明
        field_desc = QLabel('  根据字段内容拆分文件，支持时间周期拆分和级联拆分')
        field_desc.setStyleSheet('color: #7f8c8d; font-size: 12px; margin-left: 20px;')
        type_layout.addWidget(field_desc)

        # 按行数拆分选项
        self.rows_split_radio = QRadioButton('按行数拆分')
        self.rows_split_radio.setToolTip('直接按行数拆分，不考虑字段内容，适合大文件快速拆分')
        type_layout.addWidget(self.rows_split_radio)

        # 按行数拆分说明
        rows_desc = QLabel('  直接按行数拆分，不考虑字段内容，适合大文件快速拆分')
        rows_desc.setStyleSheet('color: #7f8c8d; font-size: 12px; margin-left: 20px;')
        type_layout.addWidget(rows_desc)

        self.split_type_button_group.addButton(self.field_split_radio, 0)
        self.split_type_button_group.addButton(self.rows_split_radio, 1)

        type_group.setLayout(type_layout)
        card_layout.addWidget(type_group)

        return self._create_card('', card_content)

    def _create_buttons(self):
        """创建按钮"""
        self._create_nav_buttons(show_back=False, show_next=True)

    def _on_mode_changed(self):
        """模式改变处理"""
        is_folder = self.folder_radio.isChecked()
        self.recursive_checkbox.setVisible(is_folder)
        self.browse_btn.setText('选择文件夹...' if is_folder else '浏览...')
        self.path_input.setPlaceholderText(
            '选择文件夹...' if is_folder else '选择 CSV 文件...'
        )
        self.path_input.clear()
        self.file_info_label.clear()

    def _on_browse_clicked(self):
        """浏览按钮点击处理"""
        is_folder = self.folder_radio.isChecked()

        if is_folder:
            # 选择文件夹
            folder_path = QFileDialog.getExistingDirectory(
                self,
                '选择包含 CSV 文件的文件夹',
                str(Path.home())
            )
            if folder_path:
                self._set_folder_path(folder_path)
        else:
            # 选择文件
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                '选择 CSV 文件',
                str(Path.home()),
                'CSV 文件 (*.csv);;所有文件 (*)'
            )
            if file_path:
                self._set_file_path(file_path)

    def _set_file_path(self, file_path):
        """设置文件路径"""
        self.path_input.setText(file_path)
        self.app.set_state('file_path', file_path)
        self.app.set_state('is_folder', False)
        self.app.set_state('recursive', False)

        # 显示文件信息
        try:
            # 获取文件大小
            file_size = Path(file_path).stat().st_size
            size_str = FileUtils.format_file_size(file_size)

            # 尝试读取文件获取字段数（使用自动编码检测）
            df = FileUtils.read_csv_with_encoding(file_path, encoding='auto', nrows=0)
            row_count = len(df.columns)

            self.file_info_label.setText(
                f'文件大小: {size_str} | 字段数: {row_count}'
            )
        except Exception as e:
            self.file_info_label.setText(f'文件信息: 无法读取 - {str(e)}')

    def _set_folder_path(self, folder_path):
        """设置文件夹路径"""
        self.path_input.setText(folder_path)
        self.app.set_state('file_path', folder_path)
        self.app.set_state('is_folder', True)
        self.app.set_state('recursive', self.recursive_checkbox.isChecked())

        # 显示文件信息
        try:
            csv_files = FileUtils.get_csv_files(folder_path, self.recursive_checkbox.isChecked())
            self.file_info_label.setText(f'找到 {len(csv_files)} 个 CSV 文件')
        except Exception as e:
            self.file_info_label.setText(f'文件信息: 无法读取 - {str(e)}')

    def on_activated(self):
        """页面激活时调用"""
        # 恢复之前的状态
        file_path = self.app.get_state('file_path')
        if file_path:
            self.path_input.setText(file_path)

        # 恢复拆分类型选择
        split_type = self.app.get_state('split_type', 'field')
        if split_type == 'rows':
            self.rows_split_radio.setChecked(True)
        else:
            self.field_split_radio.setChecked(True)

    def validate(self):
        """验证页面输入"""
        file_path = self.path_input.text()
        if not file_path:
            return False, '请选择文件或文件夹'

        path = Path(file_path)
        if not path.exists():
            return False, '路径不存在'

        if self.single_file_radio.isChecked():
            if path.suffix.lower() != '.csv':
                return False, '请选择 CSV 文件'
        else:
            if not path.is_dir():
                return False, '请选择有效的文件夹'

        return True, ''

    def collect_data(self):
        """收集页面数据"""
        # 获取拆分类型
        split_type = 'rows' if self.rows_split_radio.isChecked() else 'field'

        data = {
            'file_path': self.path_input.text(),
            'is_folder': self.folder_radio.isChecked(),
            'recursive': self.recursive_checkbox.isChecked(),
            'split_type': split_type,
        }

        # 保存状态到 app
        self.app.set_state('file_path', data['file_path'])
        self.app.set_state('is_folder', data['is_folder'])
        self.app.set_state('recursive', data['recursive'])
        self.app.set_state('split_type', data['split_type'])

        return data

    def get_next_page(self):
        """获取下一页"""
        split_type = self.app.get_state('split_type', 'field')
        if split_type == 'rows':
            # 按行数拆分，跳过字段配置，直接到拆分设置
            return self.main_window.PAGE_SPLIT
        else:
            # 按字段拆分，需要配置字段
            return self.main_window.PAGE_FIELD

    def get_prev_page(self):
        """获取上一页"""
        return self.main_window.PAGE_HOME
