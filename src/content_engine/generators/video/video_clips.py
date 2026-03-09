from __future__ import annotations

from pathlib import Path

from src.config.settings import settings

from .openai_client import get_openai_client
from .schemas import SceneAsset
from .utils import ensure_dir, nearest_supported_video_seconds, poll_until


def generate_motion_videos(scene_assets: list[SceneAsset], run_dir: Path) -> list[SceneAsset]:
    if not settings.video_enable_motion:
        return scene_assets

    clips_dir = ensure_dir(run_dir / "clips")
    client = get_openai_client()

    for asset in scene_assets:
        if asset.visual_type != "motion_clip":
            continue

        video = client.videos.create(
            model=settings.openai_video_model,
            prompt=asset.visual_prompt,
            size=settings.video_size,
            quality=settings.video_quality,
            seconds=nearest_supported_video_seconds(
                asset.duration_sec or settings.video_default_motion_seconds
            ),
        )

        def _poll():
            current = client.videos.retrieve(video.id)
            if current.status == "completed":
                return current
            if current.status == "failed":
                message = current.error.message if current.error else "Unknown video generation failure"
                raise RuntimeError(message)
            return None

        finished = poll_until(_poll, timeout_sec=3600, interval_sec=15)
        output_path = clips_dir / f"scene_{asset.scene_number:02d}.mp4"
        content = client.videos.download_content(finished.id)
        output_path.write_bytes(content.read())
        asset.motion_video_path = output_path

    return scene_assets
