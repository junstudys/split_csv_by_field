# CSV Splitter - 智能CSV文件拆分工具

## 功能特性

✅ 单独字段拆分（支持多字段组合）
✅ 时间字段智能识别与拆分（年/季度/月/日）
✅ 大文件自动二次拆分（默认50万行）
✅ 单文件或文件夹批量处理
✅ CLI命令行调用（基于fire库）
✅ 进度显示与详细日志
✅ 自动编码检测

## 安装依赖

```bash
pip install pandas fire tqdm chardet
```

## 快速开始

### 1. 查看文件字段
```bash
python csv_splitter.py list-fields --file data.csv
```

### 2. 按单字段拆分
```bash
python csv_splitter.py split --input data.csv --split-fields "派件网点上级"
```

### 3. 按多字段拆分（含时间）
```bash
python csv_splitter.py split \
    --input data.csv \
    --split-fields "派件网点上级,结算日期" \
    --time-period M \
    --max-rows 500000
```

### 4. 批量处理文件夹
```bash
python csv_splitter.py split \
    --input ./data/ \
    --split-fields "结算日期" \
    --time-period Q \
    --recursive
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 输入文件或文件夹路径 | 必填 |
| `--split-fields` | 拆分字段（逗号分隔） | 必填 |
| `--time-period` | 时间周期：Y/Q/M/D | M |
| `--max-rows` | 单文件最大行数 | 500000 |
| `--output` | 输出目录 | ./split_data |
| `--recursive` | 递归处理子文件夹 | False |
| `--encoding` | 文件编码 | auto |

## 示例

详见下方代码文件