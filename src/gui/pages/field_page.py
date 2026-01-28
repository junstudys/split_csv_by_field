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

        # 检查是否是目录（文件夹批量处理模式）
        if path.is_dir():
            self._load_folder_fields(path)
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

    def _load_folder_fields(self, folder_path):
        """加载文件夹中所有 CSV 文件的字段（批量处理模式）"""
        # 确保字段列表可见
        self.field_list.setVisible(True)
        # 隐藏提示卡片（如果有）
        if hasattr(self, 'hint_card') and self.hint_card is not None:
            self.hint_card.setVisible(False)

        try:
            # 获取文件夹中所有 CSV 文件
            recursive = self.app.get_state('recursive', False)
            csv_files = FileUtils.get_csv_files(str(folder_path), recursive)

            if not csv_files:
                self._show_error(f'文件夹中没有找到 CSV 文件。\n路径: {folder_path}\n\n请检查：\n1. 文件夹中是否有 .csv 文件\n2. 是否需要勾选"递归处理子文件夹"')
                return

            # 检查字段一致性
            consistency_result = self._check_folder_fields_consistency(csv_files)

            if not consistency_result['consistent']:
                # 字段不一致，显示错误
                self._show_fields_inconsistency_error(consistency_result, len(csv_files))
                return

            # 字段一致，显示字段列表
            self._display_folder_fields(
                consistency_result['fields'],
                consistency_result['field_types'],
                len(csv_files)
            )

        except Exception as e:
            self._show_error(f'文件夹读取失败: {str(e)}\n\n请检查文件夹路径是否正确')

    def _check_folder_fields_consistency(self, csv_files):
        """
        检查文件夹中所有 CSV 文件的字段一致性

        返回:
            dict: {
                'consistent': bool,  # 是否一致
                'fields': list,      # 字段列表
                'field_types': dict, # 字段类型 {field_name: 'date'/'normal'}
                'errors': list      # 错误信息列表
            }
        """
        result = {
            'consistent': True,
            'fields': None,
            'field_types': {},
            'errors': []
        }

        # 用于存储所有文件的字段信息
        all_files_info = []

        # 读取所有文件的字段信息
        for csv_file in csv_files:
            try:
                df = FileUtils.read_csv_with_encoding(csv_file, encoding='auto', nrows=1000)
                fields = list(df.columns)

                # 检测每个字段的类型
                field_types = {}
                for field in fields:
                    is_date = DateUtils.is_date_column(df[field])
                    field_types[field] = 'date' if is_date else 'normal'

                all_files_info.append({
                    'file': csv_file,
                    'fields': fields,
                    'field_types': field_types
                })
            except Exception as e:
                result['errors'].append({
                    'type': 'read_error',
                    'file': csv_file,
                    'message': str(e)
                })
                result['consistent'] = False
                return result

        # 检查字段名是否一致
        first_file_fields = all_files_info[0]['fields']
        first_file_field_set = set(first_file_fields)

        for i, file_info in enumerate(all_files_info[1:], 1):
            current_fields = file_info['fields']
            current_field_set = set(current_fields)

            # 检查字段数量
            if len(current_fields) != len(first_file_fields):
                result['consistent'] = False
                result['errors'].append({
                    'type': 'field_count_mismatch',
                    'file1': csv_files[0],
                    'file2': file_info['file'],
                    'count1': len(first_file_fields),
                    'count2': len(current_fields)
                })
                return result

            # 检查字段名
            if current_field_set != first_file_field_set:
                # 找出不一致的字段
                missing_in_current = first_file_field_set - current_field_set
                extra_in_current = current_field_set - first_file_field_set

                result['consistent'] = False
                result['errors'].append({
                    'type': 'field_name_mismatch',
                    'file1': csv_files[0],
                    'file2': file_info['file'],
                    'missing': list(missing_in_current),
                    'extra': list(extra_in_current)
                })
                return result

        # 检查字段类型是否一致
        first_file_types = all_files_info[0]['field_types']

        for i, file_info in enumerate(all_files_info[1:], 1):
            current_types = file_info['field_types']
            type_mismatches = []

            for field_name in first_file_fields:
                if first_file_types[field_name] != current_types.get(field_name):
                    type_mismatches.append({
                        'field': field_name,
                        'type1': first_file_types[field_name],
                        'type2': current_types.get(field_name)
                    })

            if type_mismatches:
                result['consistent'] = False
                result['errors'].append({
                    'type': 'field_type_mismatch',
                    'file1': csv_files[0],
                    'file2': file_info['file'],
                    'mismatches': type_mismatches
                })
                return result

        # 所有检查通过，字段一致
        result['fields'] = first_file_fields
        result['field_types'] = first_file_types
        return result

    def _show_fields_inconsistency_error(self, consistency_result, total_files):
        """显示字段不一致的错误信息"""
        errors = consistency_result['errors']
        error_parts = []

        error_parts.append('<p><b>📁 批量处理检查</b></p>')
        error_parts.append(f'<p>共扫描 {total_files} 个 CSV 文件，发现字段不一致问题：</p>')
        error_parts.append('<hr style="margin: 15px 0; border: none; border-top: 1px solid #e74c3c;">')

        for error in errors:
            error_type = error['type']

            if error_type == 'read_error':
                error_parts.append(f'''
                <p><b>❌ 文件读取错误</b></p>
                <p>文件: {error['file']}</p>
                <p>错误: {error['message']}</p>
                ''')

            elif error_type == 'field_count_mismatch':
                error_parts.append(f'''
                <p><b>❌ 字段数量不一致</b></p>
                <p>文件 1: {error['file1']} - {error['count1']} 个字段</p>
                <p>文件 2: {error['file2']} - {error['count2']} 个字段</p>
                ''')

            elif error_type == 'field_name_mismatch':
                missing = error['missing']
                extra = error['extra']

                error_parts.append(f'''
                <p><b>❌ 字段名不一致</b></p>
                <p>文件 1: {error['file1']}</p>
                <p>文件 2: {error['file2']}</p>
                ''')

                if missing:
                    error_parts.append(f'<p>文件 2 缺少字段: {", ".join(missing)}</p>')
                if extra:
                    error_parts.append(f'<p>文件 2 多余字段: {", ".join(extra)}</p>')

            elif error_type == 'field_type_mismatch':
                mismatches = error['mismatches']
                mismatch_details = []

                for m in mismatches:
                    type1_name = '📅 日期字段' if m['type1'] == 'date' else '📝 普通字段'
                    type2_name = '📅 日期字段' if m['type2'] == 'date' else '📝 普通字段'
                    mismatch_details.append(f'  • <b>{m["field"]}</b>: 文件1为{type1_name}，文件2为{type2_name}')

                error_parts.append(f'''
                <p><b>❌ 字段类型不一致</b></p>
                <p>文件 1: {error['file1']}</p>
                <p>文件 2: {error['file2']}</p>
                <p>类型不匹配的字段:</p>
                <p>{"".join(mismatch_details)}</p>
                ''')

        error_parts.append('<hr style="margin: 15px 0; border: none; border-top: 1px solid #e74c3c;">')
        error_parts.append('<p><b>💡 建议</b></p>')
        error_parts.append('<p>批量拆分要求所有 CSV 文件的字段结构完全一致。请确保：</p>')
        error_parts.append('<ul style="margin-left: 20px;">')
        error_parts.append('<li>所有文件的字段名相同</li>')
        error_parts.append('<li>对应字段的类型相同（都是日期字段或都是普通字段）</li>')
        error_parts.append('<li>字段顺序可以不同，但字段名必须一致</li>')
        error_parts.append('</ul>')

        html_message = ''.join(error_parts)

        self.field_list.clear()
        self.field_count_label.setText('字段不一致')
        self.status_label.setText(html_message)
        self.status_label.setStyleSheet('''
            color: #c0392b;
            background-color: #fadbd8;
            padding: 20px;
            border-radius: 6px;
            border: 2px solid #e74c3c;
            font-size: 14px;
        ''')
        self.status_label.setVisible(True)

    def _display_folder_fields(self, fields, field_types, file_count):
        """显示文件夹的字段列表（字段一致性检查通过）"""
        # 隐藏错误标签
        self.status_label.setVisible(False)

        # 先断开信号
        try:
            self.field_list.itemSelectionChanged.disconnect(self._update_selected_label)
        except TypeError:
            pass

        self.field_list.clear()
        self.fields = fields
        self.date_fields = []
        self.non_date_fields = []

        for field in fields:
            is_date = field_types[field] == 'date'
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

        self.field_count_label.setText(f'共 {len(fields)} 个字段（{file_count} 个文件字段一致）')

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

        # 显示成功信息
        self.status_label.setText(f'✅ 已检查 {file_count} 个 CSV 文件，字段结构一致')
        self.status_label.setStyleSheet('''
            color: #27ae60;
            background-color: #d5f4e6;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #27ae60;
            font-size: 13px;
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
