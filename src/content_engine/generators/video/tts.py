from __future__ import annotations

from pathlib import Path

from src.config.settings import settings

from .openai_client import get_openai_client
from .utils import ensure_dir


def generate_voiceover(text: str, run_dir: Path) -> Path:
    audio_dir = ensure_dir(run_dir / "audio")
    output_path = audio_dir / "voiceover.wav"

    client = get_openai_client()
    response = client.audio.speech.create(
        model=settings.openai_tts_model,
        voice=settings.openai_tts_voice,
        input=text,
        response_format="wav",
        instructions=(
            "Sound clear, premium, calm, informed, and human. "
            "Avoid hype. Speak with confident educational pacing."
        ),
    )
    output_path.write_bytes(response.read())
    return output_path
