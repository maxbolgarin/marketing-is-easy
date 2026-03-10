"""Settings API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SettingResponse(BaseModel):
    key: str
    value: str
    is_secret: bool
    label: str
    group: str
    source: str  # "database" | "environment" | "default"


class SettingsGroupResponse(BaseModel):
    group: str
    label: str
    settings: list[SettingResponse]


class SettingsUpdateRequest(BaseModel):
    settings: dict[str, str]
