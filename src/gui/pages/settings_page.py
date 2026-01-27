"""
设置页面
应用程序设置
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QWidget, QCheckBox
)
from PyQt6.QtCore import QSettings

from .base_page import BasePage


class SettingsPage(BasePage):
    """设置页面"""

    PAGE_NAME = 'settings'
    PAGE_TITLE = '设置'

    def _create_content(self):
        """创建页面内容"""
        # 默认设置卡片
        default_card = self._create_default_settings()
        self.content_layout.addWidget(default_card)

        # 添加弹性空间
        self.content_layout.addStretch(1)

        # 界面设置卡片
        ui_card = self._create_ui_settings()
        self.content_layout.addWidget(ui_card)

    def _create_default_settings(self):
        """创建默认设置"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(15)

        # 默认输出目录
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel('默认输出目录:'))
        self.default_output_input = QComboBox()
        self.default_output_input.setEditable(True)
        self.default_output_input.addItem('./split_data')
        self.default_output_input.addItem('./output')
        output_layout.addWidget(self.default_output_input)
        card_layout.addLayout(output_layout)

        # 默认编码
        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel('默认编码:'))
        self.default_encoding_combo = QComboBox()
        self.default_encoding_combo.addItems(['auto', 'utf-8', 'gbk', 'gb2312'])
        encoding_layout.addWidget(self.default_encoding_combo)
        encoding_layout.addStretch()
        card_layout.addLayout(encoding_layout)

        # 默认行数限制
        rows_layout = QHBoxLayout()
        self.enable_default_rows = QCheckBox('默认启用行数限制')
        rows_layout.addWidget(self.enable_default_rows)

        self.default_rows_spin = QSpinBox()
        self.default_rows_spin.setRange(1000, 10000000)
        self.default_rows_spin.setValue(500000)
        self.default_rows_spin.setSuffix(' 行')
        self.default_rows_spin.setEnabled(False)
        rows_layout.addWidget(self.default_rows_spin)

        self.enable_default_rows.toggled.connect(self.default_rows_spin.setEnabled)
        rows_layout.addStretch()
        card_layout.addLayout(rows_layout)

        # 默认时间周期
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel('默认时间周期:'))
        self.default_period_combo = QComboBox()
        # 顺序与 TIME_PERIODS 一致：Y, H, Q, M, HM, D
        self.default_period_combo.addItems(['Y (年)', 'H (半年)', 'Q (季度)', 'M (月)', 'HM (半月)', 'D (日)'])
        self.default_period_combo.setCurrentIndex(0)  # 默认选择年
        period_layout.addWidget(self.default_period_combo)
        period_layout.addStretch()
        card_layout.addLayout(period_layout)

        return self._create_card('默认设置', card_content)

    def _create_ui_settings(self):
        """创建界面设置"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(15)

        # 主题
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel('主题:'))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem('浅色主题', 'light')
        self.theme_combo.addItem('深色主题', 'dark')
        self.theme_combo.addItem('系统默认', 'system')
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        card_layout.addLayout(theme_layout)

        # 其他选项
        self.show_tips = QCheckBox('显示提示信息')
        self.show_tips.setChecked(True)
        card_layout.addWidget(self.show_tips)

        self.auto_preview = QCheckBox('自动预览')
        self.auto_preview.setChecked(True)
        card_layout.addWidget(self.auto_preview)

        return self._create_card('界面设置', card_content)

    def _create_buttons(self):
        """创建按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        reset_btn = QPushButton('重置默认')
        reset_btn.clicked.connect(self._on_reset_clicked)
        button_layout.addWidget(reset_btn)

        save_btn = QPushButton('保存设置')
        save_btn.setObjectName('primaryButton')
        save_btn.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton#primaryButton:hover {
                background-color: #2980b9;
            }
        """)
        save_btn.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(save_btn)

        self.button_layout.addLayout(button_layout)

    def _on_reset_clicked(self):
        """重置设置"""
        self.default_output_input.setCurrentIndex(0)
        self.default_encoding_combo.setCurrentIndex(0)
        self.enable_default_rows.setChecked(False)
        self.default_rows_spin.setValue(500000)
        self.default_period_combo.setCurrentIndex(0)  # 年
        self.theme_combo.setCurrentIndex(2)
        self.show_tips.setChecked(True)
        self.auto_preview.setChecked(True)

    def _on_save_clicked(self):
        """保存设置"""
        settings = QSettings('JunStudio', 'CSVSplitter')

        # 保存默认设置
        settings.setValue('default_output', self.default_output_input.currentText())
        settings.setValue('default_encoding', self.default_encoding_combo.currentText())
        settings.setValue('enable_default_rows', self.enable_default_rows.isChecked())
        settings.setValue('default_rows', self.default_rows_spin.value())
        settings.setValue('default_period', self.default_period_combo.currentIndex())

        # 保存界面设置
        settings.setValue('theme', self.theme_combo.currentData())
        settings.setValue('show_tips', self.show_tips.isChecked())
        settings.setValue('auto_preview', self.auto_preview.isChecked())

        # 应用设置
        self._apply_settings()

    def _apply_settings(self):
        """应用设置"""
        # TODO: 应用主题等设置
        pass

    def on_activated(self):
        """页面激活时调用"""
        # 加载保存的设置
        settings = QSettings('JunStudio', 'CSVSplitter')

        default_output = settings.value('default_output', './split_data')
        default_encoding = settings.value('default_encoding', 'auto')
        enable_default_rows = settings.value('enable_default_rows', False, type=bool)
        default_rows = settings.value('default_rows', 500000, type=int)
        default_period = settings.value('default_period', 0, type=int)
        theme = settings.value('theme', 'system')
        show_tips = settings.value('show_tips', True, type=bool)
        auto_preview = settings.value('auto_preview', True, type=bool)

        # 应用到界面
        self.default_output_input.setEditText(default_output)
        self.default_encoding_combo.setCurrentText(default_encoding)
        self.enable_default_rows.setChecked(enable_default_rows)
        self.default_rows_spin.setValue(default_rows)
        self.default_period_combo.setCurrentIndex(default_period)

        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme:
                self.theme_combo.setCurrentIndex(i)
                break

        self.show_tips.setChecked(show_tips)
        self.auto_preview.setChecked(auto_preview)
