# PDF Reading Import Script

用于把英语真题 PDF 自动导入为翻译模块可用的 JSON 数据。

## 能力

- 渲染 PDF 页面
- 对页面做 OCR（依赖 pdftoppm + tesseract）
- 自动识别 Reading Comprehension 中的 Text 1 到 Text 4
- 自动截断选择题区域，只保留文章正文
- 自动切句
- 自动做一层 OCR 清洗，修正常见错词、缩写断裂、题干串入等问题
- 可选：自动生成每句话的 zhReference 参考译文
- 生成 translation collection 可直接使用的 JSON 文件

## 脚本位置

`scripts/import_reading_from_pdf.py`

## 依赖

本脚本依赖：

- `pdftoppm`
- `tesseract`
- Python Pillow（项目环境通常已具备）

如果你要自动生成参考译文，还需要：

- 一个 OpenAI 兼容接口
- 对应 API Key，默认从环境变量 `OPENAI_API_KEY` 读取

## 基本用法

直接导入到项目内容目录：

```bash
python3 scripts/import_reading_from_pdf.py \
  --pdf "/Users/renhan/Desktop/英语文件夹/2012年真题.pdf"
```

指定输出目录：

```bash
python3 scripts/import_reading_from_pdf.py \
  --pdf "/Users/renhan/Desktop/英语文件夹/2012年真题.pdf" \
  --output-dir "tmp/generated_translation/2012" \
  --keep-temp
```

## 自动生成参考译文

先设置 API Key：

```bash
export OPENAI_API_KEY="你的密钥"
```

然后执行：

```bash
python3 scripts/import_reading_from_pdf.py \
  --pdf "/Users/renhan/Desktop/英语文件夹/2012年真题.pdf" \
  --output-dir "tmp/generated_translation/2012" \
  --generate-zh
```

如果你使用的是兼容 OpenAI 的其他网关，也可以指定：

```bash
python3 scripts/import_reading_from_pdf.py \
  --pdf "/Users/renhan/Desktop/英语文件夹/2012年真题.pdf" \
  --generate-zh \
  --translation-base-url "https://your-api.example.com/v1" \
  --translation-model "gpt-4.1-mini"
```

## 参数说明

- `--pdf`: 必填，PDF 文件路径
- `--year`: 可选，手动指定年份；默认会从文件名中识别 `2012` 这类年份
- `--output-dir`: 输出 JSON 文件目录，默认是 `src/content/translation`
- `--tmp-dir`: 中间渲染 / OCR 文件目录，默认是 `tmp/translation_import`
- `--dpi`: PDF 渲染分辨率，默认 `180`
- `--psm`: tesseract 的页面分割模式，默认 `6`
- `--keep-temp`: 保留中间文件，便于排查 OCR 问题
- `--generate-zh`: 自动生成 `zhReference`
- `--translation-model`: 自动翻译时使用的模型
- `--translation-base-url`: OpenAI 兼容接口地址
- `--translation-timeout`: 翻译请求超时时间，单位秒
- `--translation-chunk-size`: 每次翻译请求携带的句子数
- `--api-key-env`: API Key 所在环境变量名，默认 `OPENAI_API_KEY`

## 输出结果

脚本会输出 4 个 JSON 文件，格式类似：

- `2012-reading-text-1.json`
- `2012-reading-text-2.json`
- `2012-reading-text-3.json`
- `2012-reading-text-4.json`

每条句子默认结构：

- `en`: 自动提取并切句后的英文
- `zhReference`: 如果没开自动翻译，则默认填 `待补充参考译文`

## 当前效果说明

- 对英语真题扫描件有效
- Text 1-4 的正文提取已经可用
- 已增加一层 OCR 清洗，可修正常见问题，例如：
  - `put in recent years` → `but in recent years`
  - `L. A.` → `L.A.`
  - `U. S.` → `U.S.`
  - 行尾混入题目题干时自动截断
- 但 OCR 本质上仍然不是 100% 无误，所以建议流程仍然是：

1. 先跑脚本批量导入
2. 快速人工浏览一遍英文正文
3. 如有需要再微调个别 OCR 错词
4. 自动或人工补充参考译文

## 适合你现在网站的工作流

你现在这个翻译网站可以直接用这套导入流程：

1. 选一份英语真题 PDF
2. 跑脚本提取 Reading Comprehension 四篇文章
3. 自动拆句
4. 可选自动生成 `zhReference`
5. 把 JSON 放进 `src/content/translation`，页面即可直接展示

