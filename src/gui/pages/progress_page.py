"""
进度页面
显示拆分执行进度
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QWidget, QTextEdit
)

from .base_page import BasePage
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # noqa: E402
from src.gui.workers.split_worker import SplitWorker  # noqa: E402


class ProgressPage(BasePage):
    """进度页面"""

    PAGE_NAME = 'progress'
    PAGE_TITLE = '执行进度'

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.worker = None

    def _create_content(self):
        """创建页面内容"""
        # 说明区域
        info_section = self._create_section(
            '正在执行拆分',
            '请稍候，正在处理您的文件...'
        )
        self.content_layout.addWidget(info_section)

        # 进度卡片
        progress_card = self._create_progress_display()
        self.content_layout.addWidget(progress_card)

        # 添加弹性空间
        self.content_layout.addStretch(1)

        # 日志卡片
        log_card = self._create_log_display()
        self.content_layout.addWidget(log_card)

    def _create_progress_display(self):
        """创建进度显示"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(15)

        # 总体进度
        total_layout = QVBoxLayout()
        total_label = QLabel('总体进度:')
        total_label.setStyleSheet('font-weight: bold;')
        total_layout.addWidget(total_label)

        self.total_progress = QProgressBar()
        self.total_progress.setMinimum(0)
        self.total_progress.setMaximum(100)
        self.total_progress.setValue(0)
        total_layout.addWidget(self.total_progress)

        self.total_status_label = QLabel('准备中...')
        self.total_status_label.setStyleSheet('color: #7f8c8d;')
        total_layout.addWidget(self.total_status_label)

        card_layout.addLayout(total_layout)

        # 文件进度
        file_layout = QVBoxLayout()
        file_label = QLabel('当前文件:')
        file_label.setStyleSheet('font-weight: bold;')
        file_layout.addWidget(file_label)

        self.file_progress = QProgressBar()
        self.file_progress.setMinimum(0)
        self.file_progress.setMaximum(100)
        self.file_progress.setValue(0)
        file_layout.addWidget(self.file_progress)

        self.file_status_label = QLabel('')
        self.file_status_label.setStyleSheet('color: #7f8c8d;')
        file_layout.addWidget(self.file_status_label)

        card_layout.addLayout(file_layout)

        return self._create_card('', card_content)

    def _create_log_display(self):
        """创建日志显示"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
                border: 1px solid #3e3e3e;
            }
        """)
        card_layout.addWidget(self.log_text)

        return self._create_card('执行日志', card_content)

    def _create_buttons(self):
        """创建按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.setObjectName('dangerButton')
        self.cancel_btn.setStyleSheet("""
            QPushButton#dangerButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton#dangerButton:hover {
                background-color: #c0392b;
            }
        """)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)

        self.button_layout.addLayout(button_layout)

    def on_activated(self):
        """页面激活时调用"""
        self._start_split()

    def _start_split(self):
        """开始拆分"""
        # 重置界面
        self.total_progress.setValue(0)
        self.file_progress.setValue(0)
        self.total_status_label.setText('准备中...')
        self.file_status_label.setText('')
        self.log_text.clear()
        self.cancel_btn.setEnabled(True)

        # 获取配置
        config = {
            'split_type': self.app.get_state('split_type', 'field'),  # 拆分类型：按字段或按行数
            'file_path': self.app.get_state('file_path'),
            'fields': self.app.get_state('fields', []),
            'date_fields': self.app.get_state('date_fields', []),  # 日期字段列表
            'time_period': self.app.get_state('time_period'),
            'max_rows': self.app.get_state('max_rows'),
            'output_dir': self.app.get_state('output_dir', './split_data'),
            'encoding': 'auto',  # 固定为自动检测
            'is_folder': self.app.get_state('is_folder', False),
            'recursive': self.app.get_state('recursive', False),
        }

        # 创建并启动工作线程
        self.worker = SplitWorker(config)
        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._on_log)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, total_current, total_total, file_current, file_total, message):
        """进度更新"""
        # 更新总体进度
        if total_total > 0:
            total_percent = int(total_current / total_total * 100)
            self.total_progress.setValue(total_percent)

        # 更新文件进度
        if file_total > 0:
            file_percent = int(file_current / file_total * 100)
            self.file_progress.setValue(file_percent)

        # 更新状态
        self.total_status_label.setText(f'处理中... {total_current}/{total_total}')
        self.file_status_label.setText(message)

    def _on_log(self, message):
        """日志输出"""
        self.log_text.append(message)

    def _on_finished(self, result):
        """处理完成"""
        self.cancel_btn.setEnabled(False)
        self.total_progress.setValue(100)
        self.total_status_label.setText('完成!')

        # 发送完成信号
        self.app.signals.split_finished.emit(result)

    def _on_error(self, error_message):
        """处理错误"""
        self.cancel_btn.setEnabled(False)
        self.log_text.append(f'\n错误: {error_message}')

        # 发送失败信号
        self.app.signals.split_failed.emit(error_message)

    def _on_cancel_clicked(self):
        """取消按钮点击"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

            self.cancel_btn.setEnabled(False)
            self.total_status_label.setText('已取消')

            # 发送取消信号
            self.app.signals.split_cancelled.emit()
