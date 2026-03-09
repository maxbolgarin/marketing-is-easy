from __future__ import annotations

import base64
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.config.settings import settings

from .openai_client import get_openai_client
from .schemas import SceneAsset, VideoPlan
from .utils import ensure_dir


def _load_font(font_path: str | None, size: int):
    if font_path and Path(font_path).exists():
        return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


def _teal_prompt_suffix() -> str:
    return (
        " Brand through-line: teal light accents, teal highlights, teal special effects,"
        " premium clean futurism, realistic lighting, scientific wellness mood, vertical 9:16."
    )


def generate_scene_assets(plan: VideoPlan, run_dir: Path) -> list[SceneAsset]:
    images_dir = ensure_dir(run_dir / "images")
    slides_dir = ensure_dir(run_dir / "rendered_slides")

    assets: list[SceneAsset] = []
    for scene in plan.scenes:
        asset = SceneAsset(
            scene_number=scene.scene_number,
            visual_type=scene.visual_type,
            duration_sec=scene.duration_sec,
            visual_prompt=scene.visual_prompt,
            on_screen_text=scene.on_screen_text,
            subtitle_text=scene.subtitle_text,
            voiceover_chunk=scene.voiceover_chunk,
        )

        if scene.visual_type in {"motion_clip", "still_zoom", "infographic", "text_slide", "cta_slide"}:
            asset.image_path = generate_image_for_scene(
                prompt=scene.visual_prompt + _teal_prompt_suffix(),
                output_path=images_dir / f"scene_{scene.scene_number:02d}.png",
            )

        asset.rendered_slide_path = render_branded_slide(
            asset=asset,
            output_path=slides_dir / f"scene_{scene.scene_number:02d}.png",
            title=plan.title if scene.scene_number == 1 else None,
        )
        assets.append(asset)

    return assets


def generate_image_for_scene(prompt: str, output_path: Path) -> Path:
    client = get_openai_client()
    result = client.images.generate(
        model=settings.openai_image_model,
        prompt=prompt,
        size="1024x1536",
        quality="low",
        output_format="png",
    )
    image_b64 = result.data[0].b64_json
    output_path.write_bytes(base64.b64decode(image_b64))
    return output_path


def render_branded_slide(asset: SceneAsset, output_path: Path, title: str | None = None) -> Path:
    base = Image.open(asset.image_path).convert("RGBA")
    canvas = base.resize((1080, 1920))

    overlay = Image.new("RGBA", canvas.size, (6, 20, 26, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_overlay.rectangle((0, 0, 1080, 1920), fill=(6, 20, 26, 110))
    draw_overlay.rectangle((0, 1180, 1080, 1920), fill=(6, 20, 26, 165))
    draw_overlay.ellipse((720, 120, 1120, 520), fill=(83, 215, 255, 45))

    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    heading_font = _load_font(settings.brand_heading_font or None, 72)
    body_font = _load_font(settings.brand_body_font or None, 42)
    logo_font = _load_font(settings.brand_heading_font or None, 40)

    draw.text((68, 60), settings.brand_name, font=logo_font, fill=settings.brand_text_color)

    if title:
        draw.text((68, 1260), title[:68], font=heading_font, fill=settings.brand_text_color)
        body_y = 1395
    else:
        body_y = 1260

    body_text = asset.on_screen_text
    wrapped = _wrap_text(draw, body_text, body_font, max_width=860)
    draw.multiline_text(
        (68, body_y), wrapped, font=body_font, fill=settings.brand_subtle_text, spacing=14
    )

    teal_bar = Image.new("RGBA", (944, 8), (83, 215, 255, 220))
    canvas.alpha_composite(teal_bar, dest=(68, 1208))

    canvas.convert("RGB").save(output_path, format="PNG")
    return output_path


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)
