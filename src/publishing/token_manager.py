"""OAuth token management — refresh long-lived Instagram tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import structlog

from src.config.settings import settings

log = structlog.get_logger()

_INSTAGRAM_REFRESH_URL = "https://graph.instagram.com/refresh_access_token"


async def refresh_instagram_long_lived_token(access_token: str) -> dict:
    """Refresh an Instagram long-lived token (valid 60 days, must refresh before expiry).

    Args:
        access_token: Current long-lived access token.

    Returns:
        {"access_token": ..., "token_type": ..., "expires_in": <seconds>}

    Raises:
        httpx.HTTPStatusError: on API errors.
    """
    log.info("refreshing_instagram_token")

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            _INSTAGRAM_REFRESH_URL,
            params={
                "grant_type": "ig_refresh_token",
                "access_token": access_token,
            },
        )
        response.raise_for_status()
        data = response.json()

    if "error" in data:
        err = data["error"]
        raise RuntimeError(f"Instagram token refresh failed: [{err.get('code')}] {err.get('message')}")

    log.info(
        "instagram_token_refreshed",
        expires_in_days=data.get("expires_in", 0) // 86400,
    )
    return data


def token_expiry_from_response(data: dict) -> datetime:
    """Compute expiry datetime from a token refresh response."""
    expires_in = data.get("expires_in", 0)
    return datetime.now(timezone.utc) + timedelta(seconds=expires_in)
