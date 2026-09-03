from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / 'src' / 'content' / 'blog'
PUBLIC_OG_DIR = ROOT / 'public' / 'og'
POST_OG_DIR = PUBLIC_OG_DIR / 'posts'

WIDTH = 1200
HEIGHT = 630

CATEGORY_LABELS = {
    'backend': '后端开发',
    'frontend': '前端工程',
    'devops': 'DevOps',
    'database': '数据库',
}

FONT_CANDIDATES = [
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/System/Library/Fonts/STHeiti Medium.ttc',
    '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    '/Library/Fonts/Arial Unicode.ttf',
]


def pick_font_path() -> str:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError('No suitable font found for cover generation.')


FONT_PATH = pick_font_path()


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def parse_frontmatter(markdown_text: str) -> dict[str, str]:
    match = re.match(r'^---\n(.*?)\n---\n', markdown_text, re.S)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ':' not in line or line.lstrip().startswith('-'):
            continue
        key, value = line.split(':', 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def hex_to_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    if not text:
        return 0
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    current = ''
    i = 0

    while i < len(text):
        ch = text[i]
        if ch == '\n':
            if current:
                lines.append(current)
                current = ''
            i += 1
            continue

        candidate = current + ch
        if measure(draw, candidate, font) <= max_width:
            current = candidate
            i += 1
            continue

        if current:
            lines.append(current)
            current = ''
        else:
            lines.append(candidate)
            i += 1

        if len(lines) >= max_lines:
            break

    if len(lines) < max_lines and current:
        lines.append(current)

    consumed = ''.join(lines).replace('\n', '')
    original = text.replace('\n', '')
    if len(consumed) < len(original) and lines:
        last = lines[-1]
        ellipsis = '…'
        while last and measure(draw, last + ellipsis, font) > max_width:
            last = last[:-1]
        lines[-1] = (last + ellipsis) if last else ellipsis

    return lines[:max_lines]


def draw_gradient(base: Image.Image, top_color: str, bottom_color: str) -> None:
    draw = ImageDraw.Draw(base)
    top = hex_to_rgba(top_color)
    bottom = hex_to_rgba(bottom_color)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        color = tuple(lerp(top[i], bottom[i], t) for i in range(4))
        draw.line((0, y, WIDTH, y), fill=color)


def add_blur_blob(base: Image.Image, bbox: tuple[int, int, int, int], color: str, alpha: int, blur_radius: int) -> None:
    overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse(bbox, fill=hex_to_rgba(color, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(blur_radius))
    base.alpha_composite(overlay)


def add_background_details(base: Image.Image) -> None:
    add_blur_blob(base, (760, -40, 1220, 420), '#7c3aed', 82, 48)
    add_blur_blob(base, (860, 180, 1280, 680), '#2563eb', 92, 56)
    add_blur_blob(base, (-120, 360, 320, 860), '#0ea5e9', 70, 64)

    overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for x in range(680, WIDTH, 42):
        draw.line((x, 64, x, HEIGHT - 64), fill=(255, 255, 255, 18), width=1)
    for y in range(72, HEIGHT, 42):
        draw.line((640, y, WIDTH - 48, y), fill=(255, 255, 255, 18), width=1)

    draw.ellipse((758, 116, 1114, 472), outline=(255, 255, 255, 42), width=2)
    draw.ellipse((822, 168, 1208, 554), outline=(129, 140, 248, 54), width=2)
    draw.ellipse((728, 210, 1058, 540), outline=(167, 139, 250, 38), width=2)
    draw.rounded_rectangle((792, 214, 1082, 410), radius=40, outline=(255, 255, 255, 44), width=2, fill=(255, 255, 255, 10))
    base.alpha_composite(overlay)


def draw_card(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=36, fill=(9, 14, 32, 165), outline=(255, 255, 255, 42), width=2)
    draw.rounded_rectangle((x1 + 1, y1 + 1, x2 - 1, y2 - 1), radius=35, outline=(99, 102, 241, 20), width=1)


def draw_badge(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    fill=(99, 102, 241, 235),
    font_size: int = 28,
    padding_x: int = 18,
    padding_y: int = 10,
) -> tuple[int, int]:
    font = load_font(font_size)
    text_width = measure(draw, text, font)
    text_height = font_size
    rect = (x, y, x + text_width + padding_x * 2, y + text_height + padding_y * 2)
    draw.rounded_rectangle(rect, radius=22, fill=fill)
    draw.text((x + padding_x, y + max(6, padding_y - 2)), text, font=font, fill=(255, 255, 255, 255))
    return rect[2], rect[3]


def draw_multiline_text(draw: ImageDraw.ImageDraw, x: int, y: int, lines: Iterable[str], font: ImageFont.FreeTypeFont, fill, line_height: int) -> int:
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        current_y += line_height
    return current_y


def create_base_canvas() -> Image.Image:
    base = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw_gradient(base, '#0b1021', '#141b34')
    add_background_details(base)

    overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((46, 38, WIDTH - 46, HEIGHT - 38), radius=44, outline=(255, 255, 255, 34), width=2)
    base.alpha_composite(overlay)
    return base


def create_site_cover() -> None:
    image = create_base_canvas()
    draw = ImageDraw.Draw(image)

    draw_card(draw, (56, 56, 708, 574))
    small_font = load_font(28)
    brand_font = load_font(78)
    title_font = load_font(50)
    desc_font = load_font(26)
    draw.text((96, 98), 'echocode.com.cn', font=small_font, fill=(165, 180, 252, 255))
    draw.text((96, 156), 'CodeEcho', font=brand_font, fill=(255, 255, 255, 255))

    title_lines = wrap_text(draw, '沉淀技术实践，构建个人知识库', title_font, 548, 2)
    y = draw_multiline_text(draw, 96, 282, title_lines, title_font, (232, 236, 255, 255), 66)

    desc_lines = wrap_text(draw, '记录后端开发、工程实践与 AI 探索，把真实经验持续沉淀下来。', desc_font, 548, 2)
    y = draw_multiline_text(draw, 96, y + 22, desc_lines, desc_font, (191, 199, 227, 240), 40)

    badge_y = min(max(y + 18, 486), 514)
    draw_badge(draw, 96, badge_y, 'Backend · Engineering · AI', fill=(139, 92, 246, 228), font_size=24, padding_x=18, padding_y=8)

    PUBLIC_OG_DIR.mkdir(parents=True, exist_ok=True)
    image.save(PUBLIC_OG_DIR / 'site-cover.png')


def slugify_post(path: Path) -> str:
    return path.stem


def create_post_cover(markdown_path: Path) -> None:
    raw = markdown_path.read_text(encoding='utf-8')
    data = parse_frontmatter(raw)
    title = data.get('title', markdown_path.stem)
    description = data.get('description', 'CodeEcho 技术文章')
    category = CATEGORY_LABELS.get(data.get('category', ''), '技术文章')
    pub_date = data.get('pubDate', '')
    slug = slugify_post(markdown_path)

    image = create_base_canvas()
    draw = ImageDraw.Draw(image)
    draw_card(draw, (56, 56, 760, 574))

    meta_font = load_font(26)
    title_font = load_font(50)
    desc_font = load_font(26)
    footer_font = load_font(22)

    draw.text((96, 98), 'CodeEcho · 技术文章分享', font=meta_font, fill=(165, 180, 252, 255))
    draw_badge(draw, 96, 146, category, font_size=24, padding_x=16, padding_y=8)

    title_lines = wrap_text(draw, title, title_font, 612, 3)
    y = draw_multiline_text(draw, 96, 226, title_lines, title_font, (255, 255, 255, 255), 66)

    desc_lines = wrap_text(draw, description, desc_font, 612, 2)
    y = draw_multiline_text(draw, 96, y + 20, desc_lines, desc_font, (196, 204, 226, 244), 38)

    footer_y = 524
    draw.text((96, footer_y), 'echocode.com.cn', font=footer_font, fill=(129, 140, 248, 255))
    if pub_date:
        date_width = measure(draw, pub_date, footer_font)
        draw.text((712 - date_width, footer_y), pub_date, font=footer_font, fill=(148, 163, 184, 240))

    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay)
    d2.rounded_rectangle((820, 122, 1114, 458), radius=40, outline=(255, 255, 255, 32), width=2, fill=(255, 255, 255, 12))
    d2.ellipse((856, 164, 1078, 386), outline=(129, 140, 248, 76), width=4)
    d2.ellipse((900, 208, 1034, 342), outline=(167, 139, 250, 98), width=4)
    d2.arc((828, 136, 1100, 430), start=18, end=246, fill=(255, 255, 255, 52), width=3)
    d2.arc((872, 182, 1056, 386), start=210, end=20, fill=(96, 165, 250, 94), width=3)
    d2.rounded_rectangle((864, 450, 1068, 500), radius=25, fill=(99, 102, 241, 210))
    d2.text((902, 462), 'SHARE', font=load_font(26), fill=(255, 255, 255, 255))
    image.alpha_composite(overlay)

    POST_OG_DIR.mkdir(parents=True, exist_ok=True)
    image.save(POST_OG_DIR / f'{slug}.png')


def main() -> None:
    create_site_cover()
    for markdown_path in sorted(CONTENT_DIR.glob('*.md')):
        create_post_cover(markdown_path)
    print(f'Generated covers in: {PUBLIC_OG_DIR}')


if __name__ == '__main__':
    main()
