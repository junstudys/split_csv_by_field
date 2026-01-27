"""
拆分工作线程
在后台线程中执行 CSV 拆分操作
"""

from PyQt6.QtCore import QThread, pyqtSignal
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.splitter.csv_splitter import CSVSplitter
from src.utils.file_utils import FileUtils


class SplitWorker(QThread):
    """拆分工作线程"""

    # 信号定义
    progress = pyqtSignal(int, int, int, int, str)  # (total_current, total_total, file_current, file_total, message)
    log = pyqtSignal(str)  # 日志消息
    finished = pyqtSignal(dict)  # 完成信号，带结果数据
    error = pyqtSignal(str)  # 错误信号

    def __init__(self, config):
        """
        初始化工作线程

        Args:
            config: 拆分配置字典
        """
        super().__init__()
        self.config = config
        self.is_cancelled = False

    def run(self):
        """执行拆分操作"""
        try:
            # 获取配置
            split_type = self.config.get('split_type', 'field')
            file_path = self.config.get('file_path')
            fields = self.config.get('fields', [])
            time_period = self.config.get('time_period')
            max_rows = self.config.get('max_rows')
            output_dir = self.config.get('output_dir', './split_data')
            encoding = 'auto'  # 固定为自动检测
            is_folder = self.config.get('is_folder', False)
            recursive = self.config.get('recursive', False)

            # 调试：输出拆分类型
            self.log.emit(f'拆分类型: {"按行数拆分" if split_type == "rows" else "按字段拆分"}')
            if time_period:
                self.log.emit(f'时间周期设置: {time_period}')

            # 创建进度回调
            def progress_callback(current, total, message):
                if self.is_cancelled:
                    return
                # 发送进度信号
                self.progress.emit(current, total, 0, 100, message)

            # 初始化拆分器
            splitter = CSVSplitter(
                max_rows=max_rows,
                output_dir=output_dir,
                encoding=encoding,
                progress_callback=progress_callback
            )

            # 获取文件列表
            if is_folder:
                csv_files = FileUtils.get_csv_files(file_path, recursive)
                self.log.emit(f'找到 {len(csv_files)} 个 CSV 文件')
            else:
                csv_files = [Path(file_path)]

            if not csv_files:
                self.error.emit('没有找到 CSV 文件')
                return

            # 准备输出目录
            FileUtils.ensure_output_dir(output_dir)
            self.log.emit(f'输出目录: {Path(output_dir).absolute()}')

            # 处理每个文件
            total_files = len(csv_files)

            for i, csv_file in enumerate(csv_files):
                if self.is_cancelled:
                    break

                file_path_str = str(csv_file)
                self.log.emit(f'\n处理文件 [{i + 1}/{total_files}]: {csv_file.name}')

                # 发送文件进度
                self.progress.emit(i + 1, total_files, 0, 100, f'处理 {csv_file.name}...')

                # 根据拆分类型选择拆分方法
                if split_type == 'rows':
                    # 只按行数拆分
                    splitter.split_by_rows_only(file_path_str)
                else:
                    # 按字段拆分
                    splitter.split_single_file(file_path_str, fields, time_period)

            # 发送完成信号 - 使用 splitter 记录的文件列表
            result = {
                'total_files': splitter.stats['total_files'],
                'total_rows': splitter.stats['total_rows'],
                'output_files': len(splitter.stats['output_file_list']),  # 使用实际生成的文件数量
                'output_dir': output_dir,
                'files': splitter.stats['output_file_list'],  # 使用 splitter 记录的完整文件列表
                'errors': splitter.stats['errors'],
            }

            self.finished.emit(result)

        except Exception as e:
            import traceback
            error_msg = f'拆分过程中出错: {str(e)}'
            self.log.emit(traceback.format_exc())
            self.error.emit(error_msg)

    def cancel(self):
        """取消操作"""
        self.is_cancelled = True
