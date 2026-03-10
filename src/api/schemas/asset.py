"""Asset schemas."""

from __future__ import annotations

from pydantic import BaseModel


class AssetResponse(BaseModel):
    filename: str
    path: str
    url: str
    size: int
    modified_at: float
