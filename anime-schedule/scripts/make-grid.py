#!/usr/bin/env python3
"""将番剧 JSON 渲染成 Card，再按行列布局合成大图。"""
import argparse
import hashlib
import io
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_ROWS = 4
DEFAULT_COLS = 2
DEFAULT_GAP = 12
PAGE_WIDTH = 920
MIN_CARD_H = 200
COVER_RATIO = 0.30

SKILL_ROOT = Path(__file__).resolve().parents[1]
FONT_CJK = SKILL_ROOT / "scripts" / "SourceHanSansSC.otf"
FONT_LATIN = FONT_CJK
CACHE_DIR = SKILL_ROOT / "cover_cache"
OUTPUT_DIR = SKILL_ROOT / "output"


def read_input(stream=None):
    """读取 UTF-8 JSON，避免 Windows 控制台编码破坏中文。"""
    stream = stream or sys.stdin
    source = stream.buffer if hasattr(stream, "buffer") else stream
    return json.load(source)


def get_cover(url, cache_dir=CACHE_DIR):
    """下载封面，优先从缓存读取；下载失败返回 None。"""
    if not url:
        return None
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(url.encode()).hexdigest()[:12]
    cache_path = cache_dir / (key + ".jpg")
    if cache_path.exists():
        try:
            return Image.open(cache_path).convert("RGB")
        except (OSError, ValueError):
            pass
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "AstrBot/1.0"})
        image = Image.open(io.BytesIO(urllib.request.urlopen(request, timeout=10).read())).convert("RGB")
        image.save(str(cache_path), "JPEG", quality=85)
        return image
    except Exception:
        return None


def load_fonts(scale):
    title_size = max(16, round(22 * scale))
    body_size = max(13, round(16 * scale))
    meta_size = max(13, round(16 * scale))
    try:
        return (
            ImageFont.truetype(str(FONT_CJK), title_size),
            ImageFont.truetype(str(FONT_CJK), body_size),
            ImageFont.truetype(str(FONT_CJK), meta_size),
        )
    except OSError:
        fallback = ImageFont.load_default()
        return fallback, fallback, fallback


def wrap_text(text, font, max_width):
    """按像素宽度换行，保留完整文本，不截断。"""
    lines = []
    current = ""
    for char in str(text or ""):
        candidate = current + char
        bbox = font.getbbox(candidate)
        if current and bbox[2] - bbox[0] > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def line_height(font, extra):
    bbox = font.getbbox("中文Ag")
    return max(1, bbox[3] - bbox[1]) + extra


def card_metrics(anime, width, fonts):
    title_font, body_font, meta_font = fonts
    cover_width = min(140, max(80, round(width * COVER_RATIO)))
    text_width = max(40, width - cover_width - 24)
    original = anime.get("title") or anime.get("romaji") or ""
    title = anime.get("title_cn") or original or "???"
    if title == original:
        original = ""
    description = anime.get("description") or ""
    title_lines = wrap_text(title, title_font, text_width)
    original_lines = wrap_text(original, body_font, text_width) if original else []
    description_lines = wrap_text(description, body_font, text_width) if description else []
    title_step = line_height(title_font, 4)
    body_step = line_height(body_font, 3)
    meta_step = line_height(meta_font, 5)
    height = 8 + len(title_lines) * title_step + len(original_lines) * body_step
    height += meta_step + len(description_lines) * body_step + 8
    return cover_width, text_width, title_lines, original_lines, description_lines, max(MIN_CARD_H, height)


def render_card(anime, width, cache_dir=CACHE_DIR):
    """将一部番剧渲染成独立 Card 图片。"""
    scale = max(0.7, min(1.0, width / 460))
    fonts = load_fonts(scale)
    title_font, body_font, meta_font = fonts
    cover_width, text_width, title_lines, original_lines, description_lines, height = card_metrics(anime, width, fonts)
    canvas = Image.new("RGB", (width, height), (24, 24, 32))

    cover = get_cover(anime.get("cover"), cache_dir)
    if cover:
        canvas.paste(cover.resize((cover_width, height), Image.LANCZOS), (0, 0))
    else:
        ImageDraw.Draw(canvas).rectangle((0, 0, cover_width - 1, height - 1), fill=(50, 50, 60))

    draw = ImageDraw.Draw(canvas)
    text_x = cover_width + 12
    text_y = 8
    title_step = line_height(title_font, 4)
    body_step = line_height(body_font, 3)
    meta_step = line_height(meta_font, 5)
    for line in title_lines:
        draw.text((text_x, text_y), line, fill=(255, 255, 255), font=title_font)
        text_y += title_step
    for line in original_lines:
        draw.text((text_x, text_y), line, fill=(240, 240, 250), font=body_font)
        text_y += body_step

    episode = "?" if anime.get("episode") is None else anime.get("episode")
    airing_time = "未知" if not anime.get("time") else anime.get("time")
    draw.text((text_x, text_y), f"EP{episode}  |  时间 {airing_time}", fill=(240, 240, 250), font=meta_font)
    text_y += meta_step
    for line in description_lines:
        draw.text((text_x, text_y), line, fill=(255, 255, 255), font=body_font)
        text_y += body_step
    return canvas


def paginate(items, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
    if rows <= 0 or cols <= 0:
        raise ValueError("rows 和 cols 必须是正整数")
    capacity = rows * cols
    return [items[index:index + capacity] for index in range(0, len(items), capacity)]


def compose_grid(cards, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, gap=DEFAULT_GAP):
    """按行列放置独立 Card，返回一张最终大图。"""
    if rows <= 0 or cols <= 0:
        raise ValueError("rows 和 cols 必须是正整数")
    if len(cards) > rows * cols:
        raise ValueError("Card 数量超过当前页面容量")
    if not cards:
        raise ValueError("不能合成空页面")
    card_width = cards[0].width
    if any(card.width != card_width for card in cards):
        raise ValueError("同一页面的 Card 宽度必须一致")
    row_heights = [0] * rows
    for index, card in enumerate(cards):
        row_heights[index // cols] = max(row_heights[index // cols], card.height)
    page_width = cols * card_width + (cols - 1) * gap
    page_height = sum(row_heights) + max(0, min(rows, (len(cards) + cols - 1) // cols) - 1) * gap
    page = Image.new("RGB", (page_width, page_height), (24, 24, 32))
    row_y = []
    current_y = 0
    active_rows = (len(cards) + cols - 1) // cols
    for row in range(active_rows):
        row_y.append(current_y)
        current_y += row_heights[row] + gap
    for index, card in enumerate(cards):
        row, col = divmod(index, cols)
        page.paste(card, (col * (card_width + gap), row_y[row]))
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS)
    parser.add_argument("--gap", type=int, default=DEFAULT_GAP)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    args = parser.parse_args()
    data = read_input()
    if not data:
        raise SystemExit(1)
    card_width = (PAGE_WIDTH - args.gap * (args.cols - 1)) // args.cols
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for page_number, page_data in enumerate(paginate(data, args.rows, args.cols), start=1):
        cards = [render_card(item, card_width, args.cache_dir) for item in page_data]
        output = compose_grid(cards, args.rows, args.cols, args.gap)
        output_path = output_dir / f"anime_grid_{page_number}.jpg"
        output.save(str(output_path), "JPEG", quality=80)
        print(output_path)


if __name__ == "__main__":
    main()
