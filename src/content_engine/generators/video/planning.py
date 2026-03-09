from __future__ import annotations

import json
from pathlib import Path

from src.config.settings import settings

from .openai_client import get_openai_client
from .schemas import VideoSourceData, VideoPlan


def build_video_plan(source: VideoSourceData, run_dir: Path) -> VideoPlan:
    client = get_openai_client()

    target_duration = settings.video_final_target_seconds
    motion_scene_count = settings.video_motion_scene_count
    still_scene_count = settings.video_still_scene_count

    prompt = f"""
You are a premium short-form science content strategist for {settings.brand_name}, a biohacking brand.

Your job is to turn one long-form inspiration post into a 30s+ vertical short / reel script.

IMPORTANT PRODUCTION CONSTRAINTS
- final target duration: about {target_duration} seconds
- use exactly {motion_scene_count + still_scene_count + 1} scenes total
- use exactly {motion_scene_count} motion scenes
- use exactly {still_scene_count} still-image scenes
- include exactly 1 CTA/outro scene
- each scene should feel like 5-10 seconds in rhythm
- the motion-video generator later can only render 4, 8, or 12 second clips, so 8-second-friendly scene rhythm is preferred

BRAND VISUAL DIRECTION
- premium clean futurism
- science-based wellness
- realistic, elegant, high-end
- teal as a clear through-line in lighting, highlights, reflections, HUD-like glow, or special effects
- subtle blue-green accent lighting
- avoid cheesy stock-photo energy
- avoid clutter
- vertical 9:16 composition

SOURCE POST
Title: {source.title}
Language: {source.language}
Content:
{source.content}

OUTPUT RULES
- Return valid JSON only
- No markdown
- No code fences
- No extra commentary

RETURN THIS SHAPE
{{
  "title": "string",
  "hook": "string",
  "caption": "string",
  "cta": "string",
  "voiceover_script": "string",
  "scenes": [
    {{
      "scene_number": 1,
      "start_sec": 0,
      "end_sec": 8,
      "duration_sec": 8,
      "purpose": "hook|science|example|protocol|cta",
      "visual_type": "motion_clip|still_zoom|infographic|text_slide|cta_slide",
      "visual_prompt": "detailed cinematic visual prompt with teal through-line",
      "on_screen_text": "short readable text for this scene",
      "subtitle_text": "short subtitle chunk",
      "voiceover_chunk": "spoken narration for this scene"
    }}
  ]
}}
"""

    response = client.responses.create(
        model=settings.openai_text_model,
        input=prompt,
    )

    raw = response.output_text
    plan_dict = json.loads(raw)
    plan = VideoPlan.model_validate(plan_dict)
    (run_dir / "plan.json").write_text(
        json.dumps(plan_dict, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return plan
