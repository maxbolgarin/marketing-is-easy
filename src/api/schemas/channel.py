"""Channel schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ChannelResponse(BaseModel):
    id: UUID
    track: str
    platform: str
    account_name: str | None = None
    config: dict[str, Any] = {}
    is_active: bool
    token_expires_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChannelUpdateRequest(BaseModel):
    account_name: str | None = None
    config: dict[str, Any] | None = None
    is_active: bool | None = None
