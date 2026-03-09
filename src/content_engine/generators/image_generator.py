"""AI image generation via OpenRouter (httpx, modalities=["image"])."""

from __future__ import annotations

import base64
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
import structlog

from src.config.settings import settings

log = structlog.get_logger()


class ImageGenerator:
    """Generate images via OpenRouter using the image modality endpoint."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        storage_path: str | None = None,
    ):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = (base_url or settings.openrouter_base_url).rstrip("/")
        self.model = model or settings.openrouter_image_model
        self.storage_path = Path(storage_path or settings.media_storage_path)

    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        track: str | None = None,
    ) -> str:
        """Generate an image and save it locally.

        Args:
            prompt: Image generation prompt.
            aspect_ratio: "1:1" (1080x1080) or "9:16" (1080x1920) or "4:5" (1080x1350).
            track: Track name for file organization (e.g. "eu").

        Returns:
            Absolute local path to the saved image file.
        """
        log.info("generating_image", model=self.model, aspect_ratio=aspect_ratio)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "modalities": ["image"],
            "extra_body": {
                "aspect_ratio": aspect_ratio,
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://biomaxing.com",
                    "X-Title": "BioMaxing Social Marketing",
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        image_path = self._save_image(content, track=track or settings.track)

        log.info("image_generated", path=str(image_path))
        return str(image_path)

    def _save_image(self, content: str, track: str) -> Path:
        """Parse content (base64 data URI or URL) and save to disk."""
        today = datetime.now(timezone.utc).strftime("%Y/%m")
        out_dir = self.storage_path / track / today
        out_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid.uuid4())
        out_path = out_dir / f"{file_id}.jpg"

        if content.startswith("data:image"):
            # data:image/jpeg;base64,<data>
            match = re.match(r"data:image/[^;]+;base64,(.+)", content, re.DOTALL)
            if not match:
                raise ValueError(f"Unrecognised base64 image format: {content[:80]}")
            image_data = base64.b64decode(match.group(1))
            out_path.write_bytes(image_data)
        elif content.startswith("http"):
            # Some models return a URL — download it
            import urllib.request
            urllib.request.urlretrieve(content, out_path)
        else:
            # Try treating as raw base64
            try:
                image_data = base64.b64decode(content)
                out_path.write_bytes(image_data)
            except Exception as exc:
                raise ValueError(f"Cannot parse image content: {content[:80]}") from exc

        return out_path

    def local_path_to_url(self, local_path: str) -> str:
        """Convert local absolute path to public URL using media_base_url."""
        if not settings.media_base_url:
            raise RuntimeError(
                "MEDIA_BASE_URL is not configured. "
                "Set it to the public URL prefix where /app/media is served."
            )
        rel = Path(local_path).relative_to(self.storage_path)
        base = settings.media_base_url.rstrip("/")
        return f"{base}/{rel}"
