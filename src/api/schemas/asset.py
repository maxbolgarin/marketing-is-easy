"""Asset schemas."""

from __future__ import annotations

from pydantic import BaseModel


class AssetResponse(BaseModel):
    filename: str
    path: str
    url: str
    size: int
    content_type: str
    created_at: str
