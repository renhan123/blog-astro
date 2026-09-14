from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'images' / 'readme-banner.png'

WIDTH = 1600
HEIGHT = 840

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
    raise FileNotFoundError('No suitable font found.')


FONT_PATH = pick_font_path()


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def draw_gradient(base: Image.Image, top: str, bottom: str) -> None:
    draw = ImageDraw.Draw(base)
    c1 = hex_rgba(top)
    c2 = hex_rgba(bottom)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        color = tuple(lerp(c1[i], c2[i], t) for i in range(4))
        draw.line((0, y, WIDTH, y), fill=color)


def blur_blob(base: Image.Image, bbox: tuple[int, int, int, int], color: str, alpha: int, blur_radius: int) -> None:
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(bbox, fill=hex_rgba(color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur_radius))
    base.alpha_composite(layer)


def measure(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont) -> int:
    if not text:
        return 0
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, max_width: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    current = ''
    for ch in text:
        candidate = current + ch
        if measure(draw, candidate, f) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = ch
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines[:max_lines]


def multiline(draw: ImageDraw.ImageDraw, x: int, y: int, lines: list[str], f: ImageFont.FreeTypeFont, fill, line_height: int) -> int:
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=f, fill=fill)
        current_y += line_height
    return current_y


def pill(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, fill, size=24):
    f = font(size)
    tw = measure(draw, label, f)
    h = size + 24
    rect = (x, y, x + tw + 34, y + h)
    draw.rounded_rectangle(rect, radius=h // 2, fill=fill)
    draw.text((x + 17, y + 10), label, font=f, fill=(255, 255, 255, 255))
    return rect[2]


def build_banner() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw_gradient(image, '#091224', '#151f3d')

    blur_blob(image, (980, -80, 1580, 480), '#7c3aed', 95, 72)
    blur_blob(image, (1040, 190, 1660, 920), '#2563eb', 92, 86)
    blur_blob(image, (-120, 420, 420, 1040), '#0ea5e9', 62, 88)

    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((28, 28, WIDTH - 28, HEIGHT - 28), radius=42, outline=(255, 255, 255, 34), width=2)

    for x in range(1030, WIDTH - 50, 48):
        od.line((x, 86, x, HEIGHT - 86), fill=(255, 255, 255, 16), width=1)
    for y in range(96, HEIGHT - 40, 48):
        od.line((980, y, WIDTH - 70, y), fill=(255, 255, 255, 16), width=1)

    od.ellipse((1088, 140, 1450, 502), outline=(255, 255, 255, 48), width=2)
    od.ellipse((1160, 210, 1560, 610), outline=(129, 140, 248, 58), width=2)
    od.ellipse((1040, 290, 1360, 610), outline=(125, 211, 252, 40), width=2)
    od.rounded_rectangle((1126, 246, 1420, 438), radius=34, outline=(255, 255, 255, 40), width=2, fill=(255, 255, 255, 10))
    od.rounded_rectangle((1188, 478, 1506, 652), radius=30, outline=(255, 255, 255, 32), width=2, fill=(255, 255, 255, 8))
    od.line((1226, 560, 1468, 560), fill=(255, 255, 255, 32), width=2)
    od.line((1226, 598, 1410, 598), fill=(255, 255, 255, 24), width=2)
    image.alpha_composite(overlay)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((74, 74, 928, 766), radius=38, fill=(9, 14, 32, 160), outline=(255, 255, 255, 38), width=2)

    small = font(32)
    title_font = font(98)
    subtitle_font = font(58)
    body = font(28)
    mono = font(26)

    draw.text((126, 128), 'echocode.com.cn', font=small, fill=(165, 180, 252, 255))
    draw.text((126, 188), 'CodeEcho', font=title_font, fill=(255, 255, 255, 255))

    title_lines = wrap(draw, '沉淀技术实践，构建个人知识库', subtitle_font, 680, 2)
    y = multiline(draw, 126, 334, title_lines, subtitle_font, (233, 237, 255, 255), 78)

    desc = '记录后端开发、工程实践与 AI 探索，把真实经验持续沉淀下来。'
    desc_lines = wrap(draw, desc, body, 688, 3)
    y = multiline(draw, 126, y + 16, desc_lines, body, (191, 199, 227, 244), 42)

    x = 126
    y += 22
    x = pill(draw, x, y, 'Backend', (99, 102, 241, 228)) + 14
    x = pill(draw, x, y, 'Engineering', (14, 165, 233, 224)) + 14
    pill(draw, x, y, 'AI + Agent', (16, 185, 129, 222))

    draw.rounded_rectangle((126, 612, 874, 716), radius=28, fill=(255, 255, 255, 14), outline=(255, 255, 255, 30), width=2)
    draw.text((154, 638), 'Built with Astro · Markdown · RSS · Vercel Analytics', font=mono, fill=(227, 232, 255, 250))
    draw.text((154, 672), '个人博客 / 系列化内容组织 / 站内知识助手 MVP', font=mono, fill=(170, 183, 220, 245))

    image.save(OUT)
    print(OUT)


if __name__ == '__main__':
    build_banner()
