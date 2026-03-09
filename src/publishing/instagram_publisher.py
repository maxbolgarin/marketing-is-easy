"""Instagram Graph API publisher (Meta Graph API v22).

Two-step flow:
  1. Create media container → poll until status=FINISHED
  2. Publish container → returns Instagram post ID
"""

from __future__ import annotations

import asyncio

import httpx
import structlog

from src.config.settings import settings

log = structlog.get_logger()

# Max time to wait for a container to become FINISHED
_CONTAINER_POLL_TIMEOUT_S = 60
_CONTAINER_POLL_INTERVAL_S = 3


class InstagramPublishError(Exception):
    """Raised when Instagram publishing fails."""


class InstagramPublisher:
    def __init__(
        self,
        access_token: str | None = None,
        business_account_id: str | None = None,
        base_url: str | None = None,
    ):
        self.access_token = access_token or settings.instagram_access_token
        self.account_id = business_account_id or settings.instagram_business_account_id
        self.base_url = (base_url or settings.instagram_graph_api_url).rstrip("/")

        if not self.access_token:
            raise InstagramPublishError("instagram_access_token is not configured")
        if not self.account_id:
            raise InstagramPublishError("instagram_business_account_id is not configured")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def publish_photo(self, image_url: str, caption: str) -> dict:
        """Publish a photo to Instagram.

        Args:
            image_url: Publicly accessible URL of the image.
            caption: Post caption (up to 2200 chars).

        Returns:
            {"platform_post_id": ..., "platform_url": ...}
        """
        log.info("ig_publish_photo_start", account_id=self.account_id, image_url=image_url[:60])

        container_id = await self._create_photo_container(image_url, caption)
        await self._wait_for_container(container_id)
        post_id = await self._publish_container(container_id)

        platform_url = f"https://www.instagram.com/p/{post_id}/"
        log.info("ig_publish_photo_done", post_id=post_id)
        return {"platform_post_id": post_id, "platform_url": platform_url}

    async def publish_reel(self, video_url: str, caption: str, cover_url: str | None = None) -> dict:
        """Publish a Reel to Instagram.

        Args:
            video_url: Publicly accessible URL of the video (≤90s, 9:16).
            caption: Post caption.
            cover_url: Optional thumbnail image URL.

        Returns:
            {"platform_post_id": ..., "platform_url": ...}
        """
        log.info("ig_publish_reel_start", account_id=self.account_id)

        container_id = await self._create_reel_container(video_url, caption, cover_url)
        await self._wait_for_container(container_id)
        post_id = await self._publish_container(container_id)

        platform_url = f"https://www.instagram.com/reel/{post_id}/"
        log.info("ig_publish_reel_done", post_id=post_id)
        return {"platform_post_id": post_id, "platform_url": platform_url}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _create_photo_container(self, image_url: str, caption: str) -> str:
        """Step 1: Create a photo media container. Returns container_id."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/{self.account_id}/media",
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.access_token,
                },
            )
            data = self._check_response(response, "create_photo_container")
            return data["id"]

    async def _create_reel_container(
        self, video_url: str, caption: str, cover_url: str | None
    ) -> str:
        """Step 1: Create a Reels media container. Returns container_id."""
        params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": self.access_token,
        }
        if cover_url:
            params["cover_url"] = cover_url

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/{self.account_id}/media",
                params=params,
            )
            data = self._check_response(response, "create_reel_container")
            return data["id"]

    async def _wait_for_container(self, container_id: str) -> None:
        """Poll container status until FINISHED (or raise on ERROR/timeout)."""
        elapsed = 0.0
        while elapsed < _CONTAINER_POLL_TIMEOUT_S:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/{container_id}",
                    params={
                        "fields": "status_code,status",
                        "access_token": self.access_token,
                    },
                )
                data = self._check_response(response, "poll_container")

            status_code = data.get("status_code", "")
            log.debug("ig_container_status", container_id=container_id, status_code=status_code)

            if status_code == "FINISHED":
                return
            if status_code in ("ERROR", "EXPIRED"):
                raise InstagramPublishError(
                    f"Container {container_id} failed with status: {status_code}. "
                    f"Details: {data.get('status')}"
                )

            await asyncio.sleep(_CONTAINER_POLL_INTERVAL_S)
            elapsed += _CONTAINER_POLL_INTERVAL_S

        raise InstagramPublishError(
            f"Container {container_id} did not become FINISHED within {_CONTAINER_POLL_TIMEOUT_S}s"
        )

    async def _publish_container(self, container_id: str) -> str:
        """Step 3: Publish the container. Returns the Instagram post ID."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/{self.account_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
            )
            data = self._check_response(response, "publish_container")
            return data["id"]

    @staticmethod
    def _check_response(response: httpx.Response, step: str) -> dict:
        """Raise InstagramPublishError on non-2xx or API error."""
        try:
            data = response.json()
        except Exception:
            response.raise_for_status()
            return {}

        if "error" in data:
            err = data["error"]
            raise InstagramPublishError(
                f"Instagram API error at {step}: [{err.get('code')}] {err.get('message')}"
            )

        response.raise_for_status()
        return data
