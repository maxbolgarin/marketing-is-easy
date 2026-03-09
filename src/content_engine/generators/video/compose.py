from __future__ import annotations

from pathlib import Path
from typing import Iterable

from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

from src.config.settings import settings

from .schemas import SceneAsset, VideoPlan
from .utils import ensure_dir


def build_final_video(
    plan: VideoPlan,
    assets: Iterable[SceneAsset],
    voiceover_path: Path,
    subtitles_path: Path,
    run_dir: Path,
) -> tuple[Path, Path, Path]:
    final_dir = ensure_dir(run_dir / "final")
    final_video_path = final_dir / "short.mp4"
    cover_path = final_dir / "cover.jpg"
    caption_path = final_dir / "caption.txt"

    clips = []
    for asset in sorted(assets, key=lambda x: x.scene_number):
        if asset.motion_video_path and asset.motion_video_path.exists():
            clip = VideoFileClip(str(asset.motion_video_path)).subclipped(
                0, min(asset.duration_sec, 10)
            )
            clip = _fit_to_vertical(clip)
        else:
            clip = ImageClip(str(asset.rendered_slide_path)).with_duration(asset.duration_sec)
            clip = clip.resized(height=1920)
            clip = clip.with_position("center")
        clip = add_lower_caption(clip, asset.on_screen_text)
        clips.append(clip)

    merged = concatenate_videoclips(clips, method="compose")

    voice_clip = AudioFileClip(str(voiceover_path)).with_volume_scaled(settings.voice_volume)
    audio_layers = [voice_clip]

    if settings.bgm_path and Path(settings.bgm_path).exists():
        bgm = AudioFileClip(str(settings.bgm_path)).with_volume_scaled(settings.bgm_volume)
        bgm = bgm.with_duration(merged.duration)
        audio_layers.append(bgm)

    merged = merged.with_audio(CompositeAudioClip(audio_layers))
    merged.write_videofile(
        str(final_video_path),
        fps=settings.video_fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
    )

    frame = ImageClip(
        str(next(iter(sorted([a.rendered_slide_path for a in assets if a.rendered_slide_path]))))
    ).with_duration(0.1)
    frame.save_frame(str(cover_path), t=0)
    caption_path.write_text(plan.caption, encoding="utf-8")
    return final_video_path, cover_path, caption_path


def _fit_to_vertical(clip):
    clip = clip.resized(height=1920)
    if clip.w < 1080:
        clip = clip.resized(width=1080)
    return clip.cropped(x_center=clip.w / 2, y_center=clip.h / 2, width=1080, height=1920)


def add_lower_caption(base_clip, text: str):
    text = (text or "").strip()
    if not text:
        return base_clip

    font_name = (
        Path(settings.brand_body_font).stem
        if settings.brand_body_font and Path(settings.brand_body_font).exists()
        else "Arial"
    )
    txt = TextClip(
        text=text,
        font=font_name,
        font_size=42,
        color=settings.brand_text_color,
        size=(920, None),
        method="caption",
        text_align="left",
    ).with_duration(base_clip.duration)

    bar = ImageClip(_solid_color_image((944, txt.h + 56), (6, 20, 26))).with_duration(
        base_clip.duration
    )
    bar = bar.with_opacity(0.75).with_position((68, 1540))
    txt = txt.with_position((94, 1568))
    return CompositeVideoClip([base_clip, bar, txt], size=(1080, 1920))


def _solid_color_image(size: tuple[int, int], rgb: tuple[int, int, int]):
    from PIL import Image
    import tempfile

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    Image.new("RGB", size, rgb).save(tmp.name)
    return tmp.name
