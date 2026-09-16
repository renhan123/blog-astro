#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / 'src' / 'content' / 'translation'
DEFAULT_TMP_DIR = ROOT / 'tmp' / 'translation_import'

TEXT_TITLE_RE = re.compile(r'^\s*Text\s*([1-4])\s*$', re.I)
QUESTION_START_RE = re.compile(r'^\s*[\|Il]?[\(\[]?\d+[\)\.、]\s*')
OPTION_LINE_RE = re.compile(r'^\s*[\[\(]?[A-D][\]\)]')
FOOTER_RE = re.compile(r'英语.*试题|共\s*\d+\s*页|第\s*\d+\s*页', re.I)

ABBREVIATIONS = {
    'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
    'U.S.', 'U.K.', 'e.g.', 'i.e.', 'vs.', 'etc.', 'No.', 'L.A.'
}


@dataclass
class Article:
    text_no: int
    body: str


def run(cmd: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        capture_output=capture,
    )


def ensure_tool(name: str) -> None:
    from shutil import which

    if which(name) is None:
        raise SystemExit(f'Missing required tool: {name}')


def normalize_line(line: str) -> str:
    line = line.replace('\x0c', ' ')
    line = line.replace('“', '"').replace('”', '"').replace('’', "'")
    line = re.sub(r'\s+', ' ', line).strip()
    return line


def looks_like_question_line(line: str) -> bool:
    line = normalize_line(line)
    if not line:
        return False
    if QUESTION_START_RE.match(line):
        return True
    if OPTION_LINE_RE.match(line):
        return True
    if re.match(r'^\s*[\|Il]?\.\s+[A-Z]', line):
        return True
    if line.count('[A]') + line.count('[B]') + line.count('[C]') + line.count('[D]') >= 1:
        return True
    return False


def should_skip_line(line: str) -> bool:
    line = normalize_line(line)
    if not line:
        return True
    if FOOTER_RE.search(line):
        return True
    if line in {'Text 1', 'Text 2', 'Text 3', 'Text 4'}:
        return True
    return False


def render_pages(pdf_path: Path, render_dir: Path, dpi: int) -> list[Path]:
    render_dir.mkdir(parents=True, exist_ok=True)
    prefix = render_dir / 'page'
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', str(pdf_path), str(prefix)], check=True)
    return sorted(render_dir.glob('page-*.png'))


def preprocess_image(src: Path, dest: Path) -> None:
    img = Image.open(src).convert('L')
    width, height = img.size
    left = int(width * 0.12)
    top = int(height * 0.07)
    right = int(width * 0.94)
    bottom = int(height * 0.93)
    img = img.crop((left, top, right, bottom))
    img = ImageOps.autocontrast(img)
    img = img.point(lambda p: 255 if p > 195 else 0)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)


def ocr_image(image_path: Path, psm: int) -> str:
    result = run(['tesseract', str(image_path), 'stdout', '-l', 'eng', '--psm', str(psm)])
    return result.stdout


def clean_page_text(raw: str) -> list[str]:
    lines = []
    for raw_line in raw.splitlines():
        line = normalize_line(raw_line)
        if line:
            lines.append(line)
    return lines


def extract_articles(page_texts: list[list[str]]) -> list[Article]:
    articles: dict[int, list[str]] = {}
    current: int | None = None

    for page_lines in page_texts:
        idx = 0
        while idx < len(page_lines):
            line = page_lines[idx]
            title_match = TEXT_TITLE_RE.match(line)
            if title_match:
                current = int(title_match.group(1))
                articles.setdefault(current, [])
                idx += 1
                continue

            if current is None:
                idx += 1
                continue

            if should_skip_line(line):
                idx += 1
                continue

            if looks_like_question_line(line):
                current = None
                break

            articles[current].append(line)
            idx += 1

    output: list[Article] = []
    for text_no in sorted(articles):
        body = normalize_article_body(articles[text_no])
        if body:
            output.append(Article(text_no=text_no, body=body))
    return output


def normalize_article_body(lines: Iterable[str]) -> str:
    text = ' '.join(line.strip() for line in lines if line.strip())
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.;:?])', r'\1', text)
    text = re.sub(r'([a-z])\s+-\s+([a-z])', r'\1-\2', text)
    text = text.replace(' ,', ',').replace(' .', '.')
    return text.strip()


def protect_abbreviations(text: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    protected = text
    for idx, abbr in enumerate(sorted(ABBREVIATIONS, key=len, reverse=True)):
        token = f'__ABBR_{idx}__'
        mapping[token] = abbr
        protected = protected.replace(abbr, token)
    return protected, mapping


def split_sentences(text: str) -> list[str]:
    protected, mapping = protect_abbreviations(text)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"\(])', protected)
    restored = []
    for part in parts:
        sentence = part.strip()
        if not sentence:
            continue
        for token, abbr in mapping.items():
            sentence = sentence.replace(token, abbr)
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        if sentence:
            restored.append(sentence)
    return restored


def merge_short_fragments(sentences: list[str]) -> list[str]:
    merged: list[str] = []
    for sentence in sentences:
        current = sentence.strip()
        if not current:
            continue
        if merged and (len(current) <= 4 or re.fullmatch(r'[A-Z]\.?', current)):
            merged[-1] = (merged[-1] + ' ' + current).strip()
            continue
        merged.append(current)
    return merged


def slugify(value: str) -> str:
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', value.lower())).strip('-')


def build_record(*, year: str, article: Article, source_name: str) -> dict:
    sentences = merge_short_fragments(split_sentences(article.body))
    return {
        'title': f'{year} 真题 Text {article.text_no}',
        'description': f'来自 {year} 年英语真题 Reading Comprehension 的 Text {article.text_no}，由导入脚本自动提取并切句。',
        'source': f'{source_name} · Reading Comprehension',
        'author': f'{year} English Exam',
        'level': 'intermediate',
        'tags': [f'{year}真题', 'Reading Comprehension', 'Auto Import'],
        'estimatedMinutes': max(8, min(40, len(sentences) + 6)),
        'heroNote': '该篇为 PDF OCR 自动提取结果，建议导入后快速校对专有名词和个别 OCR 误差。',
        'publishedAt': f'{year}-01-01',
        'sentences': [
            {
                'id': f's{idx + 1}',
                'en': sentence,
                'zhReference': '待补充参考译文',
            }
            for idx, sentence in enumerate(sentences)
        ],
    }


def write_records(records: list[dict], output_dir: Path, year: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for record in records:
        match = re.search(r'Text\s+(\d+)', record['title'])
        text_no = match.group(1) if match else 'x'
        file_name = f'{year}-reading-text-{text_no}.json'
        path = output_dir / file_name
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        written.append(path)
    return written


def infer_year(pdf_path: Path, explicit_year: str | None) -> str:
    if explicit_year:
        return explicit_year
    match = re.search(r'(20\d{2})', pdf_path.stem)
    if not match:
        raise SystemExit('Cannot infer year from filename; please pass --year.')
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser(description='Auto extract Reading Comprehension Text 1-4 from an exam PDF and generate translation JSON files.')
    parser.add_argument('--pdf', required=True, help='Path to the exam PDF.')
    parser.add_argument('--year', help='Exam year, for example 2012.')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR), help='Directory to write translation JSON files.')
    parser.add_argument('--tmp-dir', default=str(DEFAULT_TMP_DIR), help='Directory to store rendered/OCR temp files.')
    parser.add_argument('--dpi', type=int, default=180, help='Render DPI for OCR. Default: 180.')
    parser.add_argument('--psm', type=int, default=6, help='Tesseract page segmentation mode. Default: 6.')
    parser.add_argument('--keep-temp', action='store_true', help='Keep rendered/OCR temp files.')
    args = parser.parse_args()

    print('[import] start', flush=True)
    ensure_tool('pdftoppm')
    ensure_tool('tesseract')

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f'PDF not found: {pdf_path}')

    year = infer_year(pdf_path, args.year)
    tmp_root = Path(args.tmp_dir).expanduser().resolve() / slugify(pdf_path.stem)
    render_dir = tmp_root / 'rendered'
    ocr_dir = tmp_root / 'ocr_ready'

    print(f'[import] rendering pages from {pdf_path.name}', flush=True)
    pages = render_pages(pdf_path, render_dir, args.dpi)
    print(f'[import] rendered {len(pages)} pages', flush=True)

    page_texts: list[list[str]] = []
    for page in pages:
        print(f'[import] ocr {page.name}', flush=True)
        processed = ocr_dir / page.name
        preprocess_image(page, processed)
        raw = ocr_image(processed, args.psm)
        page_texts.append(clean_page_text(raw))

    articles = extract_articles(page_texts)
    print(f'[import] extracted {len(articles)} reading texts', flush=True)
    if len(articles) != 4:
        print(f'Warning: expected 4 reading texts, extracted {len(articles)}.', file=sys.stderr)

    records = [build_record(year=year, article=article, source_name=pdf_path.name) for article in articles]
    written = write_records(records, Path(args.output_dir).expanduser().resolve(), year)

    print(json.dumps({
        'pdf': str(pdf_path),
        'year': year,
        'article_count': len(records),
        'written': [str(p) for p in written],
        'tmp_dir': str(tmp_root),
    }, ensure_ascii=False, indent=2))

    if not args.keep_temp:
        import shutil
        shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == '__main__':
    main()

