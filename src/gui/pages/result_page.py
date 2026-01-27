"""
结果页面
显示拆分执行结果
"""

import subprocess
import platform
from pathlib import Path

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QListWidget, QListWidgetItem, QAbstractItemView
)

from .base_page import BasePage


class ResultPage(BasePage):
    """结果页面"""

    PAGE_NAME = 'result'
    PAGE_TITLE = '拆分完成'

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.result_data = {}
        self.output_files = []

        # 在初始化时连接信号，而不是在 on_activated 中连接
        # 这样可以确保在信号发送前就已经建立了连接
        self.app.signals.split_finished.connect(self._on_result_received)

    def _create_content(self):
        """创建页面内容"""
        # 成功标识区域
        success_card = self._create_success_banner()
        self.content_layout.addWidget(success_card)

        # 统计卡片
        stats_card = self._create_stats_display()
        self.content_layout.addWidget(stats_card)

        # 添加弹性空间
        self.content_layout.addStretch(1)

        # 文件列表卡片
        files_card = self._create_files_list()
        self.content_layout.addWidget(files_card)

    def _create_success_banner(self):
        """创建成功标识横幅"""
        banner_widget = QWidget()
        banner_layout = QHBoxLayout(banner_widget)
        banner_layout.setContentsMargins(20, 20, 20, 20)
        banner_layout.setSpacing(20)

        # 成功图标
        icon_label = QLabel('✅')
        icon_label.setStyleSheet("""
            font-size: 64px;
        """)
        banner_layout.addWidget(icon_label)

        # 成功信息
        success_info = QWidget()
        success_layout = QVBoxLayout(success_info)
        success_layout.setSpacing(5)

        title_label = QLabel('拆分完成!')
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #27ae60;
        """)
        success_layout.addWidget(title_label)

        desc_label = QLabel('您的文件已成功拆分，可以查看结果或继续新的任务')
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
        """)
        success_layout.addWidget(desc_label)

        banner_layout.addWidget(success_info, 1)

        banner_widget.setStyleSheet("""
            QWidget {
                background-color: #d5f4e6;
                border-radius: 12px;
                border: 2px solid #27ae60;
            }
        """)

        return banner_widget

    def _create_stats_display(self):
        """创建统计显示"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(0)

        # 使用单一的 QLabel 显示所有统计信息
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            font-size: 15px;
            color: #2c3e50;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        """)
        self.stats_label.setWordWrap(True)
        # 初始化文本
        self.stats_label.setText("等待拆分结果...")
        card_layout.addWidget(self.stats_label)

        return self._create_card('统计信息', card_content)

    def _create_files_list(self):
        """创建文件列表"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(15)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.addStretch()

        self.open_folder_btn = QPushButton('📂 打开输出目录')
        self.open_folder_btn.setMinimumHeight(45)
        self.open_folder_btn.setMinimumWidth(150)
        self.open_folder_btn.setObjectName('successButton')
        self.open_folder_btn.setStyleSheet("""
            QPushButton#successButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton#successButton:hover {
                background-color: #229954;
            }
            QPushButton#successButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        toolbar.addWidget(self.open_folder_btn)

        card_layout.addLayout(toolbar)

        # 文件列表
        self.files_list = QListWidget()
        self.files_list.setMinimumHeight(200)
        self.files_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.files_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                padding: 8px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 4px;
                margin: 2px;
                font-size: 13px;
                border: 1px solid #ecf0f1;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
            QListWidget::item:selected {
                background-color: #e8f4fd;
                border-color: #3498db;
                color: #2980b9;
            }
        """)
        card_layout.addWidget(self.files_list)

        return self._create_card('输出文件列表', card_content)

    def _create_buttons(self):
        """创建按钮"""
        button_layout = QHBoxLayout()
        button_layout.addSpacing(20)

        home_btn = QPushButton('🏠 返回首页')
        home_btn.setMinimumHeight(45)
        home_btn.setMinimumWidth(140)
        home_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        home_btn.clicked.connect(self._on_home_clicked)
        button_layout.addWidget(home_btn)

        new_task_btn = QPushButton('➕ 新建任务')
        new_task_btn.setMinimumHeight(45)
        new_task_btn.setMinimumWidth(140)
        new_task_btn.setObjectName('primaryButton')
        new_task_btn.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton#primaryButton:hover {
                background-color: #2980b9;
            }
            QPushButton#primaryButton:pressed {
                background-color: #21618c;
            }
        """)
        new_task_btn.clicked.connect(self._on_new_task_clicked)
        button_layout.addWidget(new_task_btn)

        button_layout.addStretch()

        self.button_layout.addLayout(button_layout)

    def on_activated(self):
        """页面激活时调用"""
        # 不再连接信号（已在 __init__ 中连接）
        # 只清空列表，准备显示新的结果
        self.files_list.clear()

        # 如果已经有结果数据（信号已发送），直接更新显示
        if self.result_data:
            self._update_display()

    def _on_result_received(self, result):
        """接收结果"""
        self.result_data = result
        self._update_display()

    def _update_display(self):
        """更新显示"""
        result = self.result_data

        # 构建统计文本块
        input_files = result.get('total_files', 0)
        total_rows = result.get('total_rows', 0)
        output_files = result.get('output_files', 0)
        output_dir = result.get('output_dir', '')

        # 输出目录需要缩短显示
        output_dir_path = str(Path(output_dir).absolute())
        if len(output_dir_path) > 50:
            output_dir_path = '...' + output_dir_path[-47:]

        # 构建完整的统计文本
        stats_text = f"""📄 输入文件：{input_files}
📊 总行数：{total_rows:,}
✅ 输出文件：{output_files}
📁 输出目录：{output_dir_path}"""

        self.stats_label.setText(stats_text)

        # 更新文件列表
        self.output_files = result.get('files', [])
        self._update_files_list()

    def _update_files_list(self):
        """更新文件列表"""
        self.files_list.clear()

        # 先移除旧的计数标签（如果存在）
        parent_layout = self.files_list.parent().layout()
        if parent_layout.count() > 1:
            old_label = parent_layout.itemAt(1).widget()
            if old_label and isinstance(old_label, QLabel) and '共' in old_label.text():
                parent_layout.removeWidget(old_label)
                old_label.deleteLater()

        for file_info in self.output_files:
            if isinstance(file_info, tuple) and len(file_info) >= 2:
                file_name, row_count = file_info
                # 跳过无效的文件信息
                if file_name is None:
                    continue
                # 添加文件图标和更清晰的格式
                item_text = f'📄 {file_name}'
                tooltip = f'{file_name}\n行数: {row_count:,}'
            elif isinstance(file_info, str) and file_info:
                item_text = f'📄 {file_info}'
                tooltip = file_info
            else:
                # 跳过无效的文件信息
                continue

            item = QListWidgetItem(item_text)
            # 使用 tooltip 显示详细信息
            item.setToolTip(tooltip)
            self.files_list.addItem(item)

        # 如果有文件，显示提示
        if self.output_files and self.files_list.count() > 0:
            count_label = QLabel(f'📋 共 {self.files_list.count()} 个文件已生成')
            count_label.setStyleSheet('color: #7f8c8d; font-size: 12px; padding: 5px;')
            parent_layout.insertWidget(1, count_label)
        elif self.files_list.count() == 0:
            # 没有有效文件时显示提示
            no_files_label = QLabel('⚠️ 没有找到输出文件')
            no_files_label.setStyleSheet('color: #e74c3c; font-size: 13px; padding: 10px; background-color: #fadbd8; border-radius: 4px;')
            parent_layout.insertWidget(1, no_files_label)

    def _on_open_folder(self):
        """打开输出目录"""
        output_dir = self.result_data.get('output_dir', '')
        if not output_dir:
            return

        output_path = Path(output_dir).absolute()

        # 跨平台打开文件夹
        if platform.system() == 'Windows':
            subprocess.Popen(['explorer', str(output_path)])
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', str(output_path)])
        else:  # Linux
            subprocess.Popen(['xdg-open', str(output_path)])

    def _on_home_clicked(self):
        """返回首页"""
        self.app.navigate_to(self.main_window.PAGE_HOME)

    def _on_new_task_clicked(self):
        """新建任务"""
        # 重置状态
        self.app.reset_state()

        # 返回首页
        self.app.navigate_to(self.main_window.PAGE_HOME)

    def get_prev_page(self):
        """获取上一页"""
        return None  # 结果页不能返回
