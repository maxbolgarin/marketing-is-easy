"""Publish videos to YouTube as Shorts via the Data API v3."""

from __future__ import annotations

import asyncio
from pathlib import Path

import structlog
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src.config.settings import settings

log = structlog.get_logger()

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"


class YouTubePublishError(Exception):
    pass


class YouTubePublisher:
    def __init__(self):
        self.client_id = settings.youtube_client_id
        self.client_secret = settings.youtube_client_secret
        self.refresh_token = settings.youtube_refresh_token

    def _get_credentials(self) -> Credentials:
        if not self.refresh_token:
            raise YouTubePublishError("YouTube refresh token not configured")
        return Credentials(
            token=None,
            refresh_token=self.refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri="https://oauth2.googleapis.com/token",
        )

    def _upload_sync(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
    ) -> dict:
        credentials = self._get_credentials()
        youtube = build(YOUTUBE_API_SERVICE, YOUTUBE_API_VERSION, credentials=credentials)

        # Ensure #Shorts is in title or description for YouTube to recognize it
        if "#Shorts" not in title and "#Shorts" not in description:
            description = f"{description}\n\n#Shorts"

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags or [],
                "categoryId": "26",  # Howto & Style
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=10 * 1024 * 1024,  # 10 MB chunks
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                log.info("youtube_upload_progress", progress=f"{int(status.progress() * 100)}%")

        video_id = response["id"]
        log.info("youtube_published", video_id=video_id)

        return {
            "platform_post_id": video_id,
            "platform_url": f"https://youtube.com/shorts/{video_id}",
        }

    async def publish_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
    ) -> dict:
        """Upload a YouTube Short. Returns {"platform_post_id": ..., "platform_url": ...}."""
        if not Path(video_path).exists():
            raise YouTubePublishError(f"Video file not found: {video_path}")

        return await asyncio.to_thread(
            self._upload_sync, video_path, title, description, tags
        )
