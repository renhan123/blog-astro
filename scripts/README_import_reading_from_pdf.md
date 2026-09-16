# PDF Reading Import Script

用于把英语真题 PDF 自动导入为翻译模块可用的 JSON 数据。

## 能力

- 渲染 PDF 页面
- 对页面做 OCR（依赖 pdftoppm + tesseract）
- 自动识别 Reading Comprehension 中的 Text 1 到 Text 4
- 自动截断选择题区域，只保留文章正文
- 自动切句
- 生成 translation collection 可直接使用的 JSON 文件

## 脚本位置

scripts/import_reading_from_pdf.py

## 基本用法

直接导入到项目内容目录：

python3 scripts/import_reading_from_pdf.py \
  --pdf "/Users/renhan/Desktop/英语文件夹/2012年真题.pdf"

指定输出目录：

python3 scripts/import_reading_from_pdf.py \
  --pdf "/Users/renhan/Desktop/英语文件夹/2012年真题.pdf" \
  --output-dir "tmp/generated_translation/2012" \
  --keep-temp

## 参数说明

- --pdf: 必填，PDF 文件路径
- --year: 可选，手动指定年份；默认会从文件名中识别 2012 这类年份
- --output-dir: 输出 JSON 文件目录，默认是 src/content/translation
- --tmp-dir: 中间渲染 / OCR 文件目录，默认是 tmp/translation_import
- --dpi: PDF 渲染分辨率，默认 180
- --psm: tesseract 的页面分割模式，默认 6
- --keep-temp: 保留中间文件，便于排查 OCR 问题

## 输出结果

脚本会输出 4 个 JSON 文件，格式类似：

- 2012-reading-text-1.json
- 2012-reading-text-2.json
- 2012-reading-text-3.json
- 2012-reading-text-4.json

每条句子默认结构：

- en: 自动提取出的英文句子
- zhReference: 默认填 待补充参考译文

## 当前效果说明

- 对题目扫描件有效
- Text 1-4 的正文提取已经可用
- Text 4 这类清晰页效果最好
- OCR 仍可能出现个别字符错误，例如：
  - but -> put
  - most -> nost
  - L.A. 被拆成 L. A.

所以建议流程是：

1. 先跑脚本批量导入
2. 再人工快速校对正文
3. 最后补参考译文

## 后续建议增强

后续可以继续升级：

- 自动 OCR 清洗词典（常见错词纠正）
- 自动把 L. A. 合并成 L.A.
- 自动调用模型生成 zhReference
- 自动把导入结果直接写成带标题/主题标签的高质量 translation 数据

