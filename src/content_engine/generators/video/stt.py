from __future__ import annotations

from pathlib import Path

from src.config.settings import settings

from .openai_client import get_openai_client
from .utils import ensure_dir


def transcribe_to_srt(audio_path: Path, run_dir: Path) -> Path:
    subtitles_dir = ensure_dir(run_dir / "subtitles")
    output_path = subtitles_dir / "subtitles.srt"

    client = get_openai_client()
    with audio_path.open("rb") as f:
        transcript = client.audio.transcriptions.create(
            model=settings.openai_transcribe_model,
            file=f,
            response_format="srt",
        )

    if isinstance(transcript, str):
        output_path.write_text(transcript, encoding="utf-8")
    else:
        output_path.write_text(str(transcript), encoding="utf-8")
    return output_path
