"""
帮助页面
使用说明和常见问题
"""

from PyQt6.QtWidgets import QTabWidget, QTextEdit

from .base_page import BasePage


class HelpPage(BasePage):
    """帮助页面"""

    PAGE_NAME = 'help'
    PAGE_TITLE = '帮助'

    def _create_content(self):
        """创建页面内容"""
        # 创建标签页
        self.tab_widget = QTabWidget()

        # 快速入门
        quick_tab = self._create_quick_start_tab()
        self.tab_widget.addTab(quick_tab, '快速入门')

        # 使用说明
        guide_tab = self._create_guide_tab()
        self.tab_widget.addTab(guide_tab, '使用说明')

        # 常见问题
        faq_tab = self._create_faq_tab()
        self.tab_widget.addTab(faq_tab, '常见问题')

        # 关于
        about_tab = self._create_about_tab()
        self.tab_widget.addTab(about_tab, '关于')

        self.content_layout.addWidget(self.tab_widget)

    def _create_quick_start_tab(self):
        """创建快速入门标签页"""
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <h2>快速入门</h2>

        <h3>两种拆分模式</h3>
        <p>本工具支持两种拆分模式，根据您的需求选择：</p>
        <ul>
            <li><b>按字段拆分</b>：根据字段内容（如省份、日期）拆分文件</li>
            <li><b>按行数拆分</b>：直接按指定行数拆分，无需选择字段</li>
        </ul>

        <h3>按字段拆分流程</h3>
        <ol>
            <li><b>选择文件</b>：点击侧边栏的"文件选择"，选择要拆分的 CSV 文件</li>
            <li><b>选择拆分类型</b>：选择"按字段拆分"</li>
            <li><b>配置字段</b>：选择用于拆分的字段（支持多选）</li>
            <li><b>设置选项</b>：如有日期字段，可设置时间周期；可选设置行数限制</li>
            <li><b>预览确认</b>：检查配置摘要，点击"开始拆分"</li>
            <li><b>查看结果</b>：拆分完成后查看统计信息</li>
        </ol>

        <h3>按行数拆分流程</h3>
        <ol>
            <li><b>选择文件</b>：选择要拆分的 CSV 文件</li>
            <li><b>选择拆分类型</b>：选择"按行数拆分"</li>
            <li><b>设置行数</b>：设置单文件最大行数（1-10000000）</li>
            <li><b>预览确认</b>：检查配置，点击"开始拆分"</li>
            <li><b>查看结果</b>：拆分完成后查看统计信息</li>
        </ol>

        <h2>使用示例</h2>

        <h3>示例 1：按省份拆分订单数据</h3>
        <ul>
            <li>选择订单 CSV 文件</li>
            <li>选择"按字段拆分"</li>
            <li>在字段配置页面选择"省份"字段</li>
            <li>直接点击"下一步" → "开始拆分"</li>
        </ul>
        <p><b>结果</b>：生成按省份分类的文件，如 `sample_上海市.csv`、`sample_浙江省.csv`</p>

        <h3>示例 2：按月份拆分订单数据</h3>
        <ul>
            <li>选择订单 CSV 文件</li>
            <li>选择"按字段拆分"</li>
            <li>选择"订单日期"字段（会自动识别为日期字段）</li>
            <li>在拆分设置页面，时间周期选择"月"</li>
            <li>点击"开始拆分"</li>
        </ul>
        <p><b>结果</b>：生成按月份分类的文件，如 `sample_2024-01.csv`、`sample_2024-02.csv`</p>

        <h3>示例 3：按省份和月份级联拆分</h3>
        <ul>
            <li>选择订单 CSV 文件</li>
            <li>选择"按字段拆分"</li>
            <li>依次选择"省份"和"订单日期"字段（支持多选）</li>
            <li>时间周期选择"月"</li>
            <li>点击"开始拆分"</li>
        </ul>
        <p><b>结果</b>：生成按省份和月份组合分类的文件，如 `sample_上海市_2024-01.csv`</p>

        <h3>示例 4：按行数快速拆分大文件</h3>
        <ul>
            <li>选择大文件 CSV</li>
            <li>选择"按行数拆分"</li>
            <li>设置行数限制（如每 10000 行一个文件）</li>
            <li>点击"开始拆分"</li>
        </ul>
        <p><b>结果</b>：生成按行数拆分的文件，如 `sample_part1.csv`、`sample_part2.csv`</p>

        <h3>示例 5：按字段拆分 + 行数限制</h3>
        <ul>
            <li>选择订单 CSV 文件</li>
            <li>选择"按字段拆分"</li>
            <li>选择"省份"字段</li>
            <li>在拆分设置页面，勾选"按行数拆分大文件"</li>
            <li>设置行数限制（如每个省份文件最多 50000 行）</li>
            <li>点击"开始拆分"</li>
        </ul>
        <p><b>结果</b>：先按省份拆分，每个省份数据如果超过 50000 行，再按行数拆分</p>
        """)

        return content

    def _create_guide_tab(self):
        """创建使用说明标签页"""
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <h2>使用说明</h2>

        <h3>文件选择</h3>
        <ul>
            <li><b>单个文件</b>：选择一个 CSV 文件进行处理</li>
            <li><b>文件夹</b>：批量处理文件夹中的所有 CSV 文件</li>
            <li><b>递归处理</b>：处理文件夹及其子文件夹中的所有 CSV 文件</li>
        </ul>

        <h3>拆分类型</h3>
        <ul>
            <li><b>按字段拆分</b>：根据字段内容拆分文件
                <ul>
                    <li>支持单字段或多字段级联拆分</li>
                    <li>自动识别日期字段，支持时间周期拆分</li>
                    <li>可选行数限制，对大文件进行二次拆分</li>
                </ul>
            </li>
            <li><b>按行数拆分</b>：直接按指定行数拆分
                <ul>
                    <li>无需选择字段，适合快速拆分大文件</li>
                    <li>可设置 1-10000000 行的范围</li>
                    <li>文件命名：原文件名_part1.csv、part2.csv...</li>
                </ul>
            </li>
        </ul>

        <h3>字段配置</h3>
        <ul>
            <li><b>日期字段</b>：包含日期/时间信息的字段，标记为 📅
                <ul>
                    <li>自动识别多种日期格式</li>
                    <li>可选择按时间周期拆分（年、半年、季度、月、半月、日）</li>
                </ul>
            </li>
            <li><b>普通字段</b>：非日期字段，标记为 📝
                <ul>
                    <li>按字段唯一值拆分</li>
                    <li>支持多字段级联拆分</li>
                </ul>
            </li>
            <li><b>智能选择</b>：一键自动选中所有日期字段</li>
        </ul>

        <h3>拆分策略</h3>
        <ul>
            <li><b>单字段拆分</b>：按一个字段拆分（如：按省份）</li>
            <li><b>多字段级联</b>：按多个字段层级拆分（如：省 → 市 → 区）</li>
            <li><b>日期周期拆分</b>：按年、半年、季度、月、半月、日拆分</li>
            <li><b>组合拆分</b>：普通字段 + 日期字段组合拆分</li>
        </ul>

        <h3>拆分设置</h3>
        <p>拆分设置页面会根据您选择的字段动态调整：</p>
        <ul>
            <li><b>选择了日期字段</b>：显示"时间周期设置"和"行数限制设置"（两列布局）</li>
            <li><b>未选择日期字段</b>：只显示"行数限制设置"（简化版）</li>
            <li><b>按行数拆分模式</b>：只显示"行数拆分设置"</li>
        </ul>

        <h3>时间周期选项</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f0f0f0;"><th>周期</th><th>参数</th><th>说明</th><th>输出示例</th></tr>
        <tr><td>年</td><td>Y</td><td>按年份拆分</td><td>sample_2024.csv</td></tr>
        <tr><td>半年</td><td>H</td><td>按上半年/下半年拆分</td><td>sample_2024-H1.csv</td></tr>
        <tr><td>季度</td><td>Q</td><td>按季度拆分</td><td>sample_2024-Q1.csv</td></tr>
        <tr><td>月</td><td>M</td><td>按月份拆分（默认）</td><td>sample_2024-01.csv</td></tr>
        <tr><td>半月</td><td>HM</td><td>按上半月/下半月拆分</td><td>sample_2024-01-HM1.csv</td></tr>
        <tr><td>日</td><td>D</td><td>按日期拆分</td><td>sample_2024-01-15.csv</td></tr>
        </table>

        <h3>行数限制</h3>
        <p>设置单文件最大行数（范围：1-10000000）</p>
        <ul>
            <li><b>按字段拆分 + 行数限制</b>：先按字段拆分，然后对每个结果按行数二次拆分</li>
            <li><b>按行数拆分</b>：直接按指定行数拆分文件</li>
        </ul>

        <h3>输出目录</h3>
        <p>拆分后的文件将保存到指定目录。文件名根据拆分字段和时间周期自动生成。</p>

        <h3>数据持久化</h3>
        <p>工具会自动保存您的输入配置，返回修改页面时会恢复之前的选择。</p>
        """)
        # Let me not format the entire HTML string in one line

        return content

    def _create_faq_tab(self):
        """创建常见问题标签页"""
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <h2>常见问题</h2>

        <h3>Q: 为什么有些字段没有被识别为日期字段？</h3>
        <p>A: 日期字段需要至少 80% 的数据符合日期格式。如果识别不准确，可以检查数据格式是否规范。支持的日期格式包括：yyyy-MM-dd、yyyy/MM/dd、yyyyMMdd、yyyy-M-d 等。</p>

        <h3>Q: 支持哪些日期格式？</h3>
        <p>A: 支持以下格式：</p>
        <ul>
            <li>yyyyMM: 202401</li>
            <li>yyyy-MM: 2024-01</li>
            <li>yyyyMMdd: 20240115</li>
            <li>yyyy-MM-dd: 2024-01-15</li>
            <li>yyyy/MM/dd: 2024/01/15</li>
            <li>yyyy-M-d: 2024-1-15（不补零）</li>
            <li>yyyy/M/d: 2024/1/15（不补零）</li>
            <li>yyyy-MM-dd HH:mm:ss: 2024-01-15 14:30:00</li>
            <li>yyyy/MM/dd HH:mm:ss: 2024/01/15 14:30:00</li>
            <li>yyyy-MM-dd HH:mm: 2024-01-15 14:30</li>
        </ul>

        <h3>Q: 选择按字段拆分后，拆分设置页面只显示"行数限制"，没有"时间周期"选项？</h3>
        <p>A: 这是因为您选择的字段中没有日期字段。时间周期设置只在选择了日期字段时才会显示。如果您需要按时间周期拆分，请返回字段配置页面，确保至少选择一个日期字段（标记为 📅）。</p>

        <h3>Q: 拆分后文件名太长怎么办？</h3>
        <p>A: 文件名会自动限制在 100 个字符以内。特殊字符会被替换为下划线。</p>

        <h3>Q: 可以同时按多个日期字段拆分吗？</h3>
        <p>A: 目前只支持一个日期字段的时间周期拆分。如果选择多个日期字段，只有第一个日期字段会应用时间周期。</p>

        <h3>Q: 行数限制和字段拆分的优先级是什么？</h3>
        <p>A: 先按字段拆分，然后在每个拆分结果上再按行数拆分。</p>

        <h3>Q: 如何处理编码问题？</h3>
        <p>A: 工具会自动检测编码（UTF-8、GBK、GB2312 等），通常不需要手动设置。如果遇到编码问题，请检查文件是否为标准 CSV 格式。</p>

        <h3>Q: 日期为空的数据怎么处理？</h3>
        <p>A: 日期为空的数据会被保存到单独的文件中，文件名包含 "_NULL" 标记。</p>

        <h3>Q: 支持哪些文件编码？</h3>
        <p>A: 支持自动检测 UTF-8、GBK、GB2312、Latin-1 等常见编码。</p>

        <h3>Q: 我输入的行数（如 50）为什么变成 1000？</h3>
        <p>A: 这是 v2.2.0 之前的版本限制，当前版本已修复。现在支持输入 1-10000000 之间的任意数值。</p>

        <h3>Q: 我修改配置后返回，发现输入被重置了？</h3>
        <p>A: 这是 v2.2.0 之前的版本问题，当前版本已修复。所有用户输入（行数、时间周期等）都会正确保存和恢复。</p>

        <h3>Q: 按行数拆分和按字段拆分有什么区别？</h3>
        <p>A: </p>
        <ul>
            <li><b>按行数拆分</b>：直接将文件按指定行数切成多个小文件，不考虑内容，适合快速拆分大文件</li>
            <li><b>按字段拆分</b>：根据字段内容分类拆分，如按省份、按日期等，保持数据的逻辑完整性</li>
        </ul>

        <h3>Q: 可以拆分 Excel 文件吗？</h3>
        <p>A: 目前只支持 CSV 格式。如果您有 Excel 文件，请先将其另存为 CSV 格式。</p>

        <h3>Q: 批量处理多个文件时，如何避免文件名冲突？</h3>
        <p>A: 每个文件的拆分结果会保存在以原文件名命名的子目录中，不会产生冲突。</p>
        """)
        # Let me not format the entire HTML string in one line

        return content

    def _create_about_tab(self):
        """创建关于标签页"""
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <h2>关于</h2>

        <h3>CSV 智能拆分工具</h3>
        <p><b>版本：</b>2.2.0</p>
        <p><b>开发者：</b>lijun</p>

        <h3>功能特性</h3>
        <ul>
            <li>📊 按字段智能拆分 CSV 文件</li>
            <li>📅 自动识别日期字段</li>
            <li>⏰ 支持多种时间周期拆分（年、半年、季度、月、半月、日）</li>
            <li>🔗 支持多字段级联拆分</li>
            <li>📏 大文件自动二次拆分</li>
            <li>🔍 自动检测文件编码</li>
            <li>📁 批量处理文件夹</li>
            <li>🖥️ 图形界面和命令行双模式</li>
            <li>⚡ 按行数快速拆分模式</li>
            <li>💾 配置数据持久化</li>
        </ul>

        <h3>技术栈</h3>
        <ul>
            <li>PyQt6 - 图形界面</li>
            <li>pandas - 数据处理</li>
            <li>fire - 命令行接口</li>
        </ul>

        <h3>更新日志 (v2.2.0)</h3>
        <ul>
            <li>🎉 新增 PyQt6 图形界面 (GUI)</li>
            <li>✨ 新增按行数拆分模式（无需选择字段）</li>
            <li>✨ 智能字段识别（自动检测日期字段）</li>
            <li>✨ 动态 UI（根据选择自动显示/隐藏相关选项）</li>
            <li>🐛 修复用户输入值持久化问题</li>
            <li>🐛 修复小数值（<1000）无法输入的问题</li>
        </ul>

        <h3>许可证</h3>
        <p>MIT License</p>

        <h3>反馈与支持</h3>
        <p>如有问题或建议，请通过 GitHub Issues 反馈。</p>
        """)

        return content

    def on_activated(self):
        """页面激活时调用"""
        pass
