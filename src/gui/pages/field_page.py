"""
字段配置页面
允许用户选择用于拆分的字段
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView,
    QGroupBox, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize

from .base_page import BasePage
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # noqa: E402
from src.utils.file_utils import FileUtils  # noqa: E402
from src.utils.date_utils import DateUtils  # noqa: E402


class FieldPage(BasePage):
    """字段配置页面"""

    PAGE_NAME = 'field'
    PAGE_TITLE = '配置拆分字段'

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.fields = []
        self.date_fields = []
        self.non_date_fields = []

    def _create_content(self):
        """创建页面内容"""
        # 说明区域
        info_section = self._create_section(
            '选择拆分字段',
            '选择用于拆分 CSV 文件的字段。支持按日期字段或普通字段拆分。'
        )
        self.content_layout.addWidget(info_section)

        # 字段列表卡片
        field_card = self._create_field_list()
        self.content_layout.addWidget(field_card)

        # 说明卡片（简化版）
        help_card = self._create_help_info_simple()
        self.content_layout.addWidget(help_card)

    def _create_field_list(self):
        """创建字段列表"""
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setSpacing(10)

        # 错误/状态提示标签
        self.status_label = QLabel('')
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        card_layout.addWidget(self.status_label)

        # 工具栏
        toolbar = QHBoxLayout()

        self.select_all_btn = QPushButton('全选')
        self.select_all_btn.clicked.connect(self._on_select_all)
        toolbar.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton('清空')
        self.select_none_btn.clicked.connect(self._on_select_none)
        toolbar.addWidget(self.select_none_btn)

        self.auto_select_btn = QPushButton('智能选择')
        self.auto_select_btn.setToolTip('自动选择日期字段')
        self.auto_select_btn.clicked.connect(self._on_auto_select)
        toolbar.addWidget(self.auto_select_btn)

        toolbar.addStretch()

        # 字段数量
        self.field_count_label = QLabel('共 0 个字段')
        toolbar.addWidget(self.field_count_label)

        card_layout.addLayout(toolbar)

        # 字段列表
        self.field_list = QListWidget()
        self.field_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.field_list.setIconSize(QSize(24, 24))
        # 连接选择变化信号
        self.field_list.itemSelectionChanged.connect(self._update_selected_label)
        # 设置样式
        self.field_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
            }
            QListWidget::item {
                padding: 14px;
                border-radius: 4px;
                margin: 3px;
                font-size: 15px;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        # 设置字段列表的尺寸策略，让它可以扩展
        self.field_list.setMinimumHeight(400)
        self.field_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout.addWidget(self.field_list)

        # 选中的字段
        selected_group = QGroupBox('已选择的字段')
        selected_layout = QVBoxLayout()
        self.selected_fields_label = QLabel('点击下方字段列表选择字段')
        self.selected_fields_label.setWordWrap(True)
        self.selected_fields_label.setStyleSheet('color: #7f8c8d; font-size: 14px; padding: 12px; background-color: #f8f9fa; border-radius: 4px;')
        selected_layout.addWidget(self.selected_fields_label)
        selected_group.setLayout(selected_layout)
        card_layout.addWidget(selected_group)

        return self._create_card('', card_content)

    def _create_help_info_simple(self):
        """创建简化的帮助信息"""
        help_text = """
        <div style="font-size: 14px; line-height: 1.8;">
        <b>字段类型：</b>📅 日期字段（按时间拆分）| 📝 普通字段（按唯一值拆分）<br><br>
        <b>拆分策略：</b>单字段 | 多字段级联 | 字段+时间组合
        </div>
        """

        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            }
        """)

        return self._create_card('使用说明', help_label)

    def _create_buttons(self):
        """创建按钮"""
        self._create_nav_buttons(show_back=True, show_next=True)

    def on_activated(self):
        """页面激活时调用"""
        split_type = self.app.get_state('split_type', 'field')

        if split_type == 'rows':
            # 按行数拆分模式：显示说明，不加载字段
            self._show_rows_only_hint()
        else:
            # 按字段拆分模式：加载字段选择
            self._load_fields()

    def _show_rows_only_hint(self):
        """显示按行数拆分说明"""
        # 隐藏字段列表和工具栏
        self.field_list.setVisible(False)
        # 找到工具栏并隐藏（通过父组件查找）
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget and widget.objectName() == 'field_list_card':
                # 隐藏整个卡片
                widget.setVisible(False)
                break

        # 显示说明信息
        hint_text = """
        <div style="font-size: 14px; line-height: 1.8; padding: 20px;">
        <h3 style="color: #2c3e50; margin-bottom: 15px;">ℹ️ 按行数拆分无需选择字段</h3>

        <p style="color: #34495e;">按行数拆分模式会直接将文件按指定行数拆分成多个小文件，不需要选择拆分字段。</p>

        <p style="color: #34495e;"><b>拆分规则：</b></p>
        <ul style="color: #7f8c8d; margin-left: 20px;">
        <li>大文件将被拆分成多个小文件</li>
        <li>每个文件最多包含指定的行数</li>
        <li>文件命名格式：原文件名_part1.csv、原文件名_part2.csv...</li>
        </ul>

        <p style="color: #34495e; margin-top: 15px;">请点击"下一步"继续配置拆分参数（行数限制）。</p>
        </div>
        """

        hint_label = QLabel(hint_text)
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4fd;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #3498db;
            }
        """)

        # 创建或更新提示卡片
        if not hasattr(self, 'hint_label') or self.hint_label is None:
            self.hint_card = self._create_card('', hint_label)
            # 在字段列表卡片后插入提示卡片
            self.content_layout.insertWidget(1, self.hint_card)
        else:
            # 更新现有提示
            self.hint_label.setText(hint_text)

        # 更新字段计数标签
        self.field_count_label.setText('按行数拆分模式')

        # 清空已选择字段显示
        self.selected_fields_label.setText('无需选择字段')
        self.selected_fields_label.setStyleSheet('color: #7f8c8d; font-size: 14px; padding: 12px; background-color: #f8f9fa; border-radius: 4px;')

    def _load_fields(self):
        """加载文件字段"""
        file_path = self.app.get_state('file_path')
        if not file_path:
            self._show_error('请先选择文件')
            return

        from pathlib import Path  # noqa: E402
        path = Path(file_path)

        # 检查是否是目录
        if path.is_dir():
            self._show_error(f'选择的路径是目录，不是文件。\n请返回"文件选择"页面，重新选择 CSV 文件。\n当前路径: {file_path}')
            return

        # 检查文件是否存在
        if not path.exists():
            self._show_error(f'文件不存在: {file_path}\n请返回"文件选择"页面，重新选择文件。')
            return

        # 检查文件扩展名
        if path.suffix.lower() != '.csv':
            self._show_error(f'文件格式不正确，必须是 .csv 文件。\n当前文件: {file_path}')
            return

        # 确保字段列表可见（从按行数拆分模式返回时）
        self.field_list.setVisible(True)
        # 隐藏提示卡片（如果有）
        if hasattr(self, 'hint_card') and self.hint_card is not None:
            self.hint_card.setVisible(False)

        try:
            # 使用自动编码检测
            df = FileUtils.read_csv_with_encoding(file_path, encoding='auto', nrows=1000)

            # 隐藏错误标签
            self.status_label.setVisible(False)

            # 先断开信号，避免在恢复选择时触发不必要的更新
            try:
                self.field_list.itemSelectionChanged.disconnect(self._update_selected_label)
            except TypeError:
                pass  # 信号未连接，忽略

            self.field_list.clear()
            self.fields = list(df.columns)
            self.date_fields = []
            self.non_date_fields = []

            for field in self.fields:
                is_date = DateUtils.is_date_column(df[field])
                field_type = '📅 日期' if is_date else '📝 普通'

                if is_date:
                    self.date_fields.append(field)
                else:
                    self.non_date_fields.append(field)

                # 创建列表项
                item = QListWidgetItem(f'{field_type} | {field}')
                item.setData(Qt.ItemDataRole.UserRole, field)

                # 设置样式
                if is_date:
                    item.setForeground(Qt.GlobalColor.darkBlue)
                else:
                    item.setForeground(Qt.GlobalColor.darkGreen)

                self.field_list.addItem(item)

            self.field_count_label.setText(f'共 {len(self.fields)} 个字段')

            # 保存字段分类到状态
            self.app.set_state('date_fields', self.date_fields)
            self.app.set_state('non_date_fields', self.non_date_fields)

            # 恢复之前的选择
            selected_fields = self.app.get_state('fields', [])
            if selected_fields:
                for i in range(self.field_list.count()):
                    item = self.field_list.item(i)
                    field = item.data(Qt.ItemDataRole.UserRole)
                    if field in selected_fields:
                        item.setSelected(True)

            # 更新显示标签
            self._update_selected_label()

            # 重新连接信号
            self.field_list.itemSelectionChanged.connect(self._update_selected_label)

        except Exception as e:
            self._show_error(f'文件读取失败: {str(e)}\n\n请检查：\n1. 文件是否损坏\n2. 文件编码是否正确')

    def _show_error(self, message):
        """显示错误信息"""
        self.field_list.clear()
        self.field_count_label.setText('加载失败')
        self.status_label.setText(message)
        self.status_label.setStyleSheet('''
            color: #e74c3c;
            background-color: #fadbd8;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #e74c3c;
            font-size: 14px;
        ''')
        self.status_label.setVisible(True)

    def _update_selected_label(self):
        """更新选中字段标签"""
        selected_items = self.field_list.selectedItems()
        selected_fields = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in selected_items
        ]

        if selected_fields:
            self.selected_fields_label.setText(f'已选择 {len(selected_fields)} 个字段: {", ".join(selected_fields)}')
            self.selected_fields_label.setStyleSheet('color: #27ae60; font-size: 14px; padding: 12px; background-color: #d5f4e6; border-radius: 4px; border: 1px solid #27ae60;')
        else:
            self.selected_fields_label.setText('点击下方字段列表选择字段')
            self.selected_fields_label.setStyleSheet('color: #7f8c8d; font-size: 14px; padding: 12px; background-color: #f8f9fa; border-radius: 4px;')

    def _on_select_all(self):
        """全选"""
        for i in range(self.field_list.count()):
            item = self.field_list.item(i)
            item.setSelected(True)
        self._update_selected_label()

    def _on_select_none(self):
        """清空选择"""
        self.field_list.clearSelection()
        self._update_selected_label()

    def _on_auto_select(self):
        """智能选择日期字段"""
        self.field_list.clearSelection()

        for i in range(self.field_list.count()):
            item = self.field_list.item(i)
            field = item.data(Qt.ItemDataRole.UserRole)
            if field in self.date_fields:
                item.setSelected(True)

        self._update_selected_label()

    def validate(self):
        """验证页面输入"""
        split_type = self.app.get_state('split_type', 'field')

        if split_type == 'rows':
            # 按行数拆分模式，不需要验证字段选择
            return True, ''

        # 按字段拆分模式，验证是否选择了字段
        selected_items = self.field_list.selectedItems()
        if not selected_items:
            return False, '请至少选择一个拆分字段'

        return True, ''

    def collect_data(self):
        """收集页面数据"""
        split_type = self.app.get_state('split_type', 'field')

        if split_type == 'rows':
            # 按行数拆分模式，不需要收集字段数据
            return {}

        # 按字段拆分模式，收集选择的字段
        selected_items = self.field_list.selectedItems()
        fields = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in selected_items
        ]

        # 保存状态
        self.app.set_state('fields', fields)
        # date_fields 和 non_date_fields 已在 _load_fields 中保存

        return {
            'fields': fields,
            'date_fields': self.date_fields,
            'non_date_fields': self.non_date_fields,
        }

    def get_next_page(self):
        """获取下一页"""
        return self.main_window.PAGE_SPLIT

    def get_prev_page(self):
        """获取上一页"""
        return self.main_window.PAGE_FILE
