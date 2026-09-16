#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / 'src' / 'content' / 'translation'
DEFAULT_TMP_DIR = ROOT / 'tmp' / 'translation_import'
DEFAULT_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
DEFAULT_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')

TEXT_TITLE_RE = re.compile(r'^\s*Text\s*([1-4])\s*$', re.I)
QUESTION_START_RE = re.compile(r'^\s*[\|Il]?[\(\[]?\d+[\)\.]\s*')
OPTION_LINE_RE = re.compile(r'^\s*[\[\(]?[A-D][\]\)]')
FOOTER_RE = re.compile(r'英语.*试题|共\s*\d+\s*页|第\s*\d+\s*页', re.I)
QUESTION_INLINE_RE = re.compile(
    r'\b('
    r'By saying|'
    r'It can be learned from|'
    r'It can be inferred from|'
    r'The author (?:suggests|argues|implies|believes)|'
    r'The text is mainly about|'
    r'Which of the following|'
    r'According to (?:the text|Paragraph|Para\.?)|'
    r'The word .+? in (?:Paragraph|Para\.?)|'
    r'The last paragraph|'
    r'In the first paragraph'
    r')\b',
    re.I,
)

ABBREVIATIONS = {
    'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
    'U.S.', 'U.K.', 'e.g.', 'i.e.', 'vs.', 'etc.', 'No.', 'L.A.'
}

OCR_REPLACEMENTS = [
    (r'put in recent years', 'but in recent years'),
    (r'nost recently', 'most recently'),
    (r'he exception', 'the exception'),
    (r'sssentially', 'essentially'),
    (r'-ontradictory', 'contradictory'),
    (r'-omplicated', 'complicated'),
    (r'0 be', 'to be'),
    (r'nore than', 'more than'),
    (r'he tests', 'the tests'),
    (r'tt is', 'it is'),
    (r't also', 'it also'),
    (r'ather than empowering', 'rather than empowering'),
    (r'mposes a flat', 'imposes a flat'),
    (r'acrosstheboard', 'across-the-board'),
    (r'1omework', 'homework'),
    (r'ichievement', 'achievement'),
    (r'or hat teachers', 'or that teachers'),
    (r'esponsible for setting educational policy', 'responsible for setting educational policy'),
    (r'1earings', 'hearings'),
    (r'-onnection', 'connection'),
    (r'-vidence', 'evidence'),
    (r'gut according', 'but according'),
    (r'lomestic', 'domestic'),
    (r'ink was', 'pink was'),
    (r'ind faithfulness', 'and faithfulness'),
    (r'ige and', 'age and'),
    (r'ame into', 'came into'),
    (r'lefined', 'defined'),
    (r's natural to kids', 'is natural to kids'),
    (r'Tums out', 'Turns out'),
    (r'hould create', 'should create'),
    (r'vas only', 'was only'),
    (r'roadly accepted', 'broadly accepted'),
    (r'evertinier ategories', 'ever-tinier categories'),
    (r'egment a market', 'segment a market'),
    (r'reviously exist', 'previously exist'),
    (r'twoyearolds', 'two-year-olds'),
    (r'colourcoded', 'colour-coded'),
    (r'genderneutral', 'gender-neutral'),
    (r'»overturned', 'overturned'),
    (r'vertumed', 'overturned'),
    (r'wo genes', 'two genes'),
    (r'emain rather busy', 'remain rather busy'),
    (r'irguments against', 'arguments against'),
    (r'yene patents', 'gene patents'),
    (r'iccess to genetic tests', 'access to genetic tests'),
    (r'ederal task-force', 'federal task-force'),
    (r'ederal taskforce', 'federal task-force'),
    (r'nad won patents', 'had won patents'),
    (r'nolecule', 'molecule'),
    (r'rom cotton seeds', 'from cotton seeds'),
    (r'For xample', 'For example'),
    (r'ndividual genes', 'individual genes'),
    (r'Sompanies', 'Companies'),
    (r'ilready patented', 'already patented'),
    (r'ooking for correlations', 'looking for correlations'),
    (r"1 drug's efficacy", "a drug's efficacy"),
    (r'xplains Hans Sauer', 'explains Hans Sauer'),
    (r'‘convention', 'a convention'),
    (r'atents\.', 'patents.'),
    (r'meanspirited', 'mean-spirited'),
    (r'Antiimmigrant', 'Anti-immigrant'),
    (r'Intemet', 'Internet'),
    (r'extend\.,', 'extend.'),
    (r'L\. A\.', 'L.A.'),
    (r'U\. S\.', 'U.S.'),
    (r'tthe', 'the'),
    (r'rrather', 'rather'),
    (r'iimposes', 'imposes'),
    (r'rresponsible', 'responsible'),
    (r'iit', 'it'),
    (r'ppink', 'pink'),
    (r'ccame', 'came'),
    (r'iis', 'is'),
    (r'he toddler', 'the toddler'),
    (r'esearch', 'research'),
    (r'istorian', 'historian'),
    (r'nanufacturers', 'manufacturers'),
    (r'sshould', 'should'),
    (r'bbroadly', 'broadly'),
    (r'ssegment', 'segment'),
    (r'ppreviously', 'previously'),
    (r'ttwo', 'two'),
    (r'rremain', 'remain'),
    (r'ffederal', 'federal'),
    (r'ffrom', 'from'),
    (r'iindividual', 'individual'),
    (r'llooking', 'looking'),
    (r'eexplains', 'explains'),
    (r'ppatents', 'patents'),
    (r'a rade group', 'a trade group'),
    (r'decadesby 2005', 'decades—by 2005'),
    (r'moleculesmost are', 'molecules—most are'),
    (r'cross themespecially', 'cross them—especially'),
    (r'differencesor invent', 'differences—or invent'),
    (r'tthe toddler', 'the toddler'),
    (r'hhhistorian', 'historian'),
    (r'rrresearch', 'research'),
    (r'hhistorian', 'historian'),
    (r'evertinier categories', 'ever-tinier categories'),
    (r'surefire', 'sure-fire'),
    (r'rresearch', 'research'),
    (r'a\"preliminary step\"', 'a "preliminary step"'),
    (r'a\"third stepping stone\"', 'a "third stepping stone"'),
    (r'after\"toddler\"', 'after "toddler"'),
    (r'for\"connecting the dots,\"', 'for "connecting the dots,"'),
    (r'molecule\"is no less', 'molecule "is no less'),
]

@dataclass
class Article:
    text_no: int
    body: str

def run(cmd: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=capture)

def ensure_tool(name: str) -> None:
    from shutil import which
    if which(name) is None:
        raise SystemExit(f'Missing required tool: {name}')

def normalize_line(line: str) -> str:
    line = line.replace('\x0c', ' ')
    line = line.replace('“', '"').replace('”', '"').replace('’', "'")
    return re.sub(r'\s+', ' ', line).strip()

def looks_like_question_line(line: str) -> bool:
    line = normalize_line(line)
    if not line:
        return False
    if QUESTION_START_RE.match(line) or OPTION_LINE_RE.match(line):
        return True
    if re.match(r'^\s*[\|Il]?\.\s+[A-Z]', line):
        return True
    return line.count('[A]') + line.count('[B]') + line.count('[C]') + line.count('[D]') >= 1

def should_skip_line(line: str) -> bool:
    line = normalize_line(line)
    if not line:
        return True
    if FOOTER_RE.search(line):
        return True
    return line in {'Text 1', 'Text 2', 'Text 3', 'Text 4'}

def truncate_inline_question(line: str) -> tuple[str, bool]:
    normalized = normalize_line(line)
    match = QUESTION_INLINE_RE.search(normalized)
    if not match:
        return normalized, False
    kept = normalized[:match.start()].rstrip(' _,-.;:')
    return kept, True

def render_pages(pdf_path: Path, render_dir: Path, dpi: int) -> list[Path]:
    render_dir.mkdir(parents=True, exist_ok=True)
    prefix = render_dir / 'page'
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', str(pdf_path), str(prefix)], check=True)
    return sorted(render_dir.glob('page-*.png'))

def preprocess_image(src: Path, dest: Path) -> None:
    img = Image.open(src).convert('L')
    width, height = img.size
    crop = (int(width * 0.12), int(height * 0.07), int(width * 0.94), int(height * 0.93))
    img = img.crop(crop)
    img = ImageOps.autocontrast(img)
    img = img.point(lambda p: 255 if p > 195 else 0)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)

def ocr_image(image_path: Path, psm: int) -> str:
    return run(['tesseract', str(image_path), 'stdout', '-l', 'eng', '--psm', str(psm)]).stdout

def clean_page_text(raw: str) -> list[str]:
    return [normalize_line(line) for line in raw.splitlines() if normalize_line(line)]

def extract_articles(page_texts: list[list[str]]) -> list[Article]:
    articles: dict[int, list[str]] = {}
    current: int | None = None
    for page_lines in page_texts:
        idx = 0
        while idx < len(page_lines):
            line = page_lines[idx]
            match = TEXT_TITLE_RE.match(line)
            if match:
                current = int(match.group(1))
                articles.setdefault(current, [])
                idx += 1
                continue
            if current is None:
                idx += 1
                continue
            if should_skip_line(line):
                idx += 1
                continue
            kept, has_inline_question = truncate_inline_question(line)
            if has_inline_question:
                if kept:
                    articles[current].append(kept)
                current = None
                break
            if looks_like_question_line(line):
                current = None
                break
            articles[current].append(line)
            idx += 1
    result = []
    for text_no in sorted(articles):
        body = normalize_article_body(articles[text_no])
        if body:
            result.append(Article(text_no=text_no, body=body))
    return result

def normalize_article_body(lines: list[str]) -> str:
    text = ' '.join(line.strip() for line in lines if line.strip())
    text = text.replace('—', '-').replace('–', '-').replace('“', '"').replace('”', '"').replace('’', "'")
    text = text.replace('»', ' ').replace('«', ' ').replace('_', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.;:?])', r'\1', text)
    text = re.sub(r'([A-Za-z])\s+-\s+([A-Za-z])', r'\1-\2', text)
    text = re.sub(r'\b-([A-Za-z])', r'\1', text)
    text = text.replace('L. A.', 'L.A.')
    text = text.replace('U. S.', 'U.S.')
    text = re.sub(r'\b([A-Z])\.\s+([A-Z])\.', r'\1.\2.', text)
    for pattern, replacement in OCR_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.I)
    text = re.sub(r'([A-Za-z])\"([A-Za-z])', r'\1 \" \2', text)
    text = text.replace('\\"', "")
    text = re.sub(r"\s+([\"'\),.;:!?])", r'\1', text)
    text = re.sub(r'([,;:!?])(\w)', r'\1 \2', text)
    text = re.sub(r'(?<=[a-z0-9])\.(?=[A-Z])', '. ', text)
    text = re.sub(r'\s+', ' ', text)
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
    protected = protected.replace('...', '__ELLIPSIS__')
    parts = re.split(r"(?<=[.!?][\"'])\s+(?=[A-Za-z\(])|(?<=[.!?])\s+(?=[A-Za-z\"\(])", protected)
    restored = []
    for part in parts:
        sentence = part.strip()
        if not sentence:
            continue
        for token, abbr in mapping.items():
            sentence = sentence.replace(token, abbr)
        sentence = sentence.replace('__ELLIPSIS__', '...')
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
        if merged and (len(current) <= 4 or re.fullmatch(r'[A-Z]\.?', current) or re.search(r'(?:\b[A-Z]\.\s*){1,3}$', merged[-1])):
            merged[-1] = (merged[-1] + ' ' + current).strip()
            continue
        merged.append(current)
    return merged

def postprocess_sentence(sentence: str) -> str:
    cleaned, _ = truncate_inline_question(sentence)
    cleaned = normalize_article_body([cleaned])
    cleaned = cleaned.strip(' _')
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned

def build_record(year: str, article: Article, source_name: str) -> dict:
    sentences = [postprocess_sentence(item) for item in merge_short_fragments(split_sentences(article.body))]
    sentences = [item for item in sentences if item]
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
        'sentences': [{'id': f's{idx + 1}', 'en': sentence, 'zhReference': '待补充参考译文'} for idx, sentence in enumerate(sentences)],
    }

def extract_message_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                parts.append(item.get('text', ''))
        return ''.join(parts)
    return str(content)

def strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?', '', text).strip()
        if text.endswith('```'):
            text = text[:-3].strip()
    return text

def call_translation_api(batch: list[dict[str, str]], model: str, api_key: str, base_url: str, timeout: int) -> dict[str, str]:
    payload = {
        'model': model,
        'temperature': 0.2,
        'response_format': {'type': 'json_object'},
        'messages': [
            {'role': 'system', 'content': 'You are a careful English-to-Simplified-Chinese translator for exam reading passages. Translate faithfully and output only JSON.'},
            {'role': 'user', 'content': 'Translate each sentence into natural Simplified Chinese and return strict JSON in the format {"translations":[{"id":"s1","zh":"..."}]}.\n\n' + json.dumps(batch, ensure_ascii=False)},
        ],
    }
    url = base_url.rstrip('/') + '/chat/completions'
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='ignore')
        raise SystemExit(f'Translation API HTTPError: {exc.code} {detail}')
    except urllib.error.URLError as exc:
        raise SystemExit(f'Translation API URLError: {exc}')
    data = json.loads(raw)
    content = extract_message_text(data['choices'][0]['message']['content'])
    parsed = json.loads(strip_json_fence(content))
    result: dict[str, str] = {}
    for item in parsed.get('translations', []):
        sid = str(item.get('id', '')).strip()
        zh = str(item.get('zh', '')).strip()
        if sid:
            result[sid] = zh
    return result

def maybe_generate_translations(records: list[dict], enabled: bool, model: str, api_key: str | None, base_url: str, timeout: int, chunk_size: int, api_key_env_name: str) -> None:
    if not enabled:
        return
    if not api_key:
        raise SystemExit(f'Missing API key for translation generation. Set {api_key_env_name} before running with --generate-zh.')
    for record in records:
        sentences = record.get('sentences', [])
        generated: dict[str, str] = {}
        for start in range(0, len(sentences), chunk_size):
            batch = [{'id': item['id'], 'en': item['en']} for item in sentences[start:start + chunk_size]]
            generated.update(call_translation_api(batch, model, api_key, base_url, timeout))
        for item in sentences:
            if item['id'] in generated and generated[item['id']]:
                item['zhReference'] = generated[item['id']]

def write_records(records: list[dict], output_dir: Path, year: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for record in records:
        match = re.search(r'Text\s+(\d+)', record['title'])
        text_no = match.group(1) if match else 'x'
        path = output_dir / f'{year}-reading-text-{text_no}.json'
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
    parser.add_argument('--generate-zh', action='store_true', help='Generate zhReference automatically via an OpenAI-compatible API.')
    parser.add_argument('--translation-model', default=DEFAULT_MODEL, help='Model used for zhReference generation.')
    parser.add_argument('--translation-base-url', default=DEFAULT_BASE_URL, help='Base URL for the OpenAI-compatible API.')
    parser.add_argument('--translation-timeout', type=int, default=120, help='HTTP timeout in seconds for translation generation.')
    parser.add_argument('--translation-chunk-size', type=int, default=12, help='Sentence batch size for each translation API request.')
    parser.add_argument('--api-key-env', default='OPENAI_API_KEY', help='Environment variable that stores the API key. Default: OPENAI_API_KEY')
    args = parser.parse_args()

    print('[import] start', flush=True)
    ensure_tool('pdftoppm')
    ensure_tool('tesseract')
    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f'PDF not found: {pdf_path}')
    year = infer_year(pdf_path, args.year)
    slug = re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', pdf_path.stem.lower())).strip('-') or year
    tmp_root = Path(args.tmp_dir).expanduser().resolve() / slug
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
        page_texts.append(clean_page_text(ocr_image(processed, args.psm)))
    articles = extract_articles(page_texts)
    print(f'[import] extracted {len(articles)} reading texts', flush=True)
    if len(articles) != 4:
        print(f'Warning: expected 4 reading texts, extracted {len(articles)}.', file=sys.stderr)
    records = [build_record(year, article, pdf_path.name) for article in articles]
    if args.generate_zh:
        print('[import] generating zhReference via API', flush=True)
        maybe_generate_translations(records, True, args.translation_model, os.environ.get(args.api_key_env), args.translation_base_url, args.translation_timeout, args.translation_chunk_size, args.api_key_env)
    written = write_records(records, Path(args.output_dir).expanduser().resolve(), year)
    print(json.dumps({'pdf': str(pdf_path), 'year': year, 'article_count': len(records), 'written': [str(p) for p in written], 'tmp_dir': str(tmp_root), 'generated_zh': bool(args.generate_zh)}, ensure_ascii=False, indent=2))
    if not args.keep_temp:
        shutil.rmtree(tmp_root, ignore_errors=True)

if __name__ == '__main__':
    main()
