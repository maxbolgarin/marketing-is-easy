"""Async orchestrator for the full video generation pipeline."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import structlog

from src.config.settings import settings

from .compose import build_final_video
from .planning import build_video_plan
from .schemas import VideoSourceData
from .stt import transcribe_to_srt
from .tts import generate_voiceover
from .utils import ensure_dir, slugify, timestamp_id
from .video_clips import generate_motion_videos
from .visuals import generate_scene_assets

log = structlog.get_logger()


def _build_run_dir(track: str, post_id: str) -> Path:
    """Create a run directory under media storage for this video generation."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    date_path = now.strftime("%Y/%m")
    run_name = f"{timestamp_id()}_{slugify(post_id[:8])}"
    run_dir = Path(settings.media_storage_path) / track / date_path / "video" / run_name
    return ensure_dir(run_dir)


async def generate_video_pipeline(
    post_id: uuid.UUID,
    title: str,
    content: str,
    language: str = "en",
    track: str = "eu",
) -> tuple[Path, Path, str]:
    """Run the full video generation pipeline.

    Returns (video_path, cover_path, caption).
    All sync-heavy steps are run via asyncio.to_thread.
    """
    source = VideoSourceData(
        post_id=str(post_id),
        title=title,
        language=language,
        content=content,
    )

    run_dir = _build_run_dir(track, str(post_id))
    log.info("video_pipeline_start", post_id=str(post_id), run_dir=str(run_dir))

    log.info("video_pipeline_step", step="1/6 planning")
    plan = await asyncio.to_thread(build_video_plan, source, run_dir)

    log.info("video_pipeline_step", step="2/6 generating scene visuals")
    scene_assets = await asyncio.to_thread(generate_scene_assets, plan, run_dir)

    log.info("video_pipeline_step", step="3/6 generating motion clips")
    scene_assets = await asyncio.to_thread(generate_motion_videos, scene_assets, run_dir)

    log.info("video_pipeline_step", step="4/6 generating voiceover")
    voiceover_path = await asyncio.to_thread(generate_voiceover, plan.voiceover_script, run_dir)

    log.info("video_pipeline_step", step="5/6 transcribing subtitles")
    subtitles_path = await asyncio.to_thread(transcribe_to_srt, voiceover_path, run_dir)

    log.info("video_pipeline_step", step="6/6 composing final video")
    final_video_path, cover_path, caption_path = await asyncio.to_thread(
        build_final_video, plan, scene_assets, voiceover_path, subtitles_path, run_dir,
    )

    caption = caption_path.read_text(encoding="utf-8")
    log.info("video_pipeline_done", post_id=str(post_id), video=str(final_video_path))
    return final_video_path, cover_path, caption
