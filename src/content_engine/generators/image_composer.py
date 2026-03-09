"""Pillow-based branded card composer for Instagram/social media posts."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import structlog

log = structlog.get_logger()

# BioMaxing brand palette
COLOR_BG_DARK = "#0d1b2a"       # very dark navy
COLOR_BG_PRIMARY = "#1a2744"    # deep blue
COLOR_ACCENT = "#00c4b4"        # teal accent
COLOR_ACCENT_LIGHT = "#4dd9cc"  # lighter teal for highlights
COLOR_WHITE = "#ffffff"
COLOR_GREY = "#b0bec5"

CANVAS_SQUARE = (1080, 1080)
CANVAS_PORTRAIT = (1080, 1350)

# Relative path from project root to fonts dir
FONTS_DIR = Path(__file__).parent.parent.parent.parent / "templates" / "fonts"


def _get_fonts():
    """Lazy import PIL and load fonts. Returns (regular_font_factory, bold_font_factory)."""
    from PIL import ImageFont

    regular_path = FONTS_DIR / "Roboto-Regular.ttf"
    bold_path = FONTS_DIR / "Roboto-Bold.ttf"

    def load(path: Path, size: int):
        if path.exists():
            return ImageFont.truetype(str(path), size)
        # Fallback to PIL default (no nice rendering, but won't crash)
        return ImageFont.load_default()

    return load, regular_path, bold_path


def _make_gradient_bg(size: Tuple[int, int]) -> "PIL.Image.Image":
    """Create a vertical gradient background from COLOR_BG_DARK to COLOR_BG_PRIMARY."""
    from PIL import Image
    import struct

    w, h = size
    img = Image.new("RGB", (w, h))
    pixels = img.load()

    top = tuple(int(COLOR_BG_DARK.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    bot = tuple(int(COLOR_BG_PRIMARY.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    for y in range(h):
        ratio = y / h
        r = int(top[0] + (bot[0] - top[0]) * ratio)
        g = int(top[1] + (bot[1] - top[1]) * ratio)
        b = int(top[2] + (bot[2] - top[2]) * ratio)
        for x in range(w):
            pixels[x, y] = (r, g, b)

    return img


def _draw_accent_bar(draw, x: int, y: int, w: int = 6, h: int = 60) -> None:
    """Draw a teal vertical accent bar."""
    accent_rgb = tuple(int(COLOR_ACCENT.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    draw.rectangle([x, y, x + w, y + h], fill=accent_rgb)


def _wrap_text(text: str, font, max_width: int, draw) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test_line = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


class ImageComposer:
    """Compose branded image cards using Pillow."""

    def __init__(self, storage_path: str | None = None, brand_name: str | None = None):
        from src.config.settings import settings
        self.storage_path = Path(storage_path or settings.media_storage_path)
        self.brand_name = brand_name or settings.brand_name

    def _out_path(self, track: str) -> Path:
        from src.config.settings import settings
        today = datetime.now(timezone.utc).strftime("%Y/%m")
        out_dir = self.storage_path / (track or settings.track) / today
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / f"{uuid.uuid4()}.jpg"

    def compose_tip_card(self, title: str, body: str, track: str | None = None) -> str:
        """Educational tip card: gradient bg + title + body text.

        Returns absolute path to saved JPEG.
        """
        from PIL import Image, ImageDraw

        load, reg_path, bold_path = _get_fonts()
        size = CANVAS_SQUARE
        img = _make_gradient_bg(size)
        draw = ImageDraw.Draw(img)

        margin = 80
        max_w = size[0] - 2 * margin

        # Brand name (top)
        font_brand = load(reg_path, 32)
        brand_color = tuple(int(COLOR_ACCENT.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        draw.text((margin, margin), self.brand_name.upper(), font=font_brand, fill=brand_color)

        # Accent bar
        _draw_accent_bar(draw, margin, margin + 55, w=5, h=50)

        # Title
        font_title = load(bold_path, 68)
        title_lines = _wrap_text(title, font_title, max_w, draw)
        y_cursor = margin + 130
        white_rgb = tuple(int(COLOR_WHITE.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        for line in title_lines:
            draw.text((margin, y_cursor), line, font=font_title, fill=white_rgb)
            bbox = draw.textbbox((0, 0), line, font=font_title)
            y_cursor += bbox[3] - bbox[1] + 12

        # Divider line
        y_cursor += 20
        grey_rgb = tuple(int(COLOR_GREY.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        draw.line([(margin, y_cursor), (size[0] - margin, y_cursor)], fill=grey_rgb, width=1)
        y_cursor += 30

        # Body text
        font_body = load(reg_path, 44)
        body_lines = _wrap_text(body, font_body, max_w, draw)
        for line in body_lines:
            draw.text((margin, y_cursor), line, font=font_body, fill=white_rgb)
            bbox = draw.textbbox((0, 0), line, font=font_body)
            y_cursor += bbox[3] - bbox[1] + 10

        # Bottom brand tag
        font_tag = load(reg_path, 28)
        tag = f"@{self.brand_name.lower()}"
        draw.text((margin, size[1] - margin - 30), tag, font=font_tag, fill=brand_color)

        out = self._out_path(track or "")
        img.save(str(out), "JPEG", quality=92)
        log.info("tip_card_composed", path=str(out))
        return str(out)

    def compose_quote_card(self, quote: str, track: str | None = None) -> str:
        """Dark quote card with large text centred vertically.

        Returns absolute path to saved JPEG.
        """
        from PIL import Image, ImageDraw

        load, reg_path, bold_path = _get_fonts()
        size = CANVAS_SQUARE

        # Very dark solid bg
        dark_rgb = tuple(int(COLOR_BG_DARK.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        img = Image.new("RGB", size, dark_rgb)
        draw = ImageDraw.Draw(img)

        margin = 100
        max_w = size[0] - 2 * margin

        font_quote = load(bold_path, 56)
        white_rgb = tuple(int(COLOR_WHITE.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        accent_rgb = tuple(int(COLOR_ACCENT.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

        # Quote marks
        font_big = load(bold_path, 120)
        draw.text((margin - 20, size[1] // 2 - 200), "\u201c", font=font_big, fill=accent_rgb)

        # Quote text (centred block)
        lines = _wrap_text(quote, font_quote, max_w, draw)
        total_h = sum(
            draw.textbbox((0, 0), l, font=font_quote)[3] - draw.textbbox((0, 0), l, font=font_quote)[1] + 14
            for l in lines
        )
        y_cursor = (size[1] - total_h) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_quote)
            line_w = bbox[2] - bbox[0]
            x = (size[0] - line_w) // 2
            draw.text((x, y_cursor), line, font=font_quote, fill=white_rgb)
            y_cursor += bbox[3] - bbox[1] + 14

        # Brand bottom
        font_brand = load(reg_path, 30)
        brand_text = f"— {self.brand_name}"
        bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
        bw = bbox[2] - bbox[0]
        draw.text(((size[0] - bw) // 2, size[1] - 100), brand_text, font=font_brand, fill=accent_rgb)

        out = self._out_path(track or "")
        img.save(str(out), "JPEG", quality=92)
        log.info("quote_card_composed", path=str(out))
        return str(out)

    def compose_fact_card(self, fact: str, label: str = "DID YOU KNOW?", track: str | None = None) -> str:
        """Fact highlight card with teal top bar.

        Returns absolute path to saved JPEG.
        """
        from PIL import Image, ImageDraw

        load, reg_path, bold_path = _get_fonts()
        size = CANVAS_SQUARE
        img = _make_gradient_bg(size)
        draw = ImageDraw.Draw(img)

        margin = 80
        max_w = size[0] - 2 * margin
        white_rgb = tuple(int(COLOR_WHITE.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        accent_rgb = tuple(int(COLOR_ACCENT.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

        # Teal top bar
        draw.rectangle([0, 0, size[0], 12], fill=accent_rgb)

        # Label
        font_label = load(bold_path, 36)
        draw.text((margin, 60), label, font=font_label, fill=accent_rgb)

        # Fact text (large, vertically centred)
        font_fact = load(bold_path, 62)
        lines = _wrap_text(fact, font_fact, max_w, draw)
        total_h = sum(
            draw.textbbox((0, 0), l, font=font_fact)[3] - draw.textbbox((0, 0), l, font=font_fact)[1] + 16
            for l in lines
        )
        y_cursor = (size[1] - total_h) // 2
        for line in lines:
            draw.text((margin, y_cursor), line, font=font_fact, fill=white_rgb)
            bbox = draw.textbbox((0, 0), line, font=font_fact)
            y_cursor += bbox[3] - bbox[1] + 16

        # Bottom teal bar + brand
        draw.rectangle([0, size[1] - 70, size[0], size[1]], fill=accent_rgb)
        font_brand = load(bold_path, 30)
        dark_rgb = tuple(int(COLOR_BG_DARK.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        draw.text((margin, size[1] - 52), self.brand_name.upper(), font=font_brand, fill=dark_rgb)

        out = self._out_path(track or "")
        img.save(str(out), "JPEG", quality=92)
        log.info("fact_card_composed", path=str(out))
        return str(out)
