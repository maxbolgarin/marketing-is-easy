from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel


VisualType = Literal["motion_clip", "still_zoom", "infographic", "text_slide", "cta_slide"]


class VideoSourceData(BaseModel):
    """Input data for the video pipeline (replaces Supabase SourcePost)."""
    post_id: str
    title: str
    language: str = "en"
    content: str


class ScenePlan(BaseModel):
    scene_number: int
    start_sec: int
    end_sec: int
    duration_sec: int
    purpose: str
    visual_type: VisualType
    visual_prompt: str
    on_screen_text: str
    subtitle_text: str
    voiceover_chunk: str


class VideoPlan(BaseModel):
    title: str
    hook: str
    caption: str
    cta: str
    voiceover_script: str
    scenes: list[ScenePlan]


class SceneAsset(BaseModel):
    scene_number: int
    visual_type: VisualType
    duration_sec: int
    visual_prompt: str
    on_screen_text: str
    subtitle_text: str
    voiceover_chunk: str
    image_path: Optional[Path] = None
    motion_video_path: Optional[Path] = None
    rendered_slide_path: Optional[Path] = None


class RunArtifacts(BaseModel):
    run_dir: Path
    plan_path: Path
    scenes_path: Path
    voiceover_path: Path
    subtitles_path: Path
    final_video_path: Path
    cover_path: Path
    caption_path: Path
