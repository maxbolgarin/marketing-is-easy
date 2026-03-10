"""Settings management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.deps import get_db
from src.api.schemas.common import MessageResponse
from src.api.schemas.settings import (
    SettingResponse,
    SettingsGroupResponse,
    SettingsUpdateRequest,
)
from src.config.settings import settings
from src.config.settings_registry import (
    CONFIGURABLE_SETTINGS,
    GROUP_LABELS,
    GROUP_ORDER,
)
from src.db.models import ApiUser
from src.db.settings_repo import SettingsRepo

router = APIRouter()


def _mask(value: str) -> str:
    """Mask a secret value, showing only the last 4 characters."""
    if len(value) <= 4:
        return "****"
    return "****" + value[-4:]


def _is_masked(value: str) -> bool:
    """Check if a value is the masked placeholder."""
    return value.startswith("****")


@router.get("", response_model=list[SettingsGroupResponse])
async def get_settings(
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    """Return all configurable settings grouped by category."""
    repo = SettingsRepo(db)
    db_values = await repo.get_all()

    groups: dict[str, list[SettingResponse]] = {g: [] for g in GROUP_ORDER}

    for key, meta in CONFIGURABLE_SETTINGS.items():
        db_val = db_values.get(key)
        env_val = str(getattr(settings._base, key, ""))

        if db_val is not None and db_val != "":
            source = "database"
            raw_value = db_val
        elif env_val and env_val != "0":
            source = "environment"
            raw_value = env_val
        else:
            source = "default"
            raw_value = ""

        display_value = _mask(raw_value) if meta.is_secret and raw_value else raw_value

        if meta.group not in groups:
            groups[meta.group] = []

        groups[meta.group].append(
            SettingResponse(
                key=key,
                value=display_value,
                is_secret=meta.is_secret,
                label=meta.label,
                group=meta.group,
                source=source,
            )
        )

    return [
        SettingsGroupResponse(
            group=g,
            label=GROUP_LABELS.get(g, g),
            settings=groups[g],
        )
        for g in GROUP_ORDER
        if groups.get(g)
    ]


@router.put("", response_model=MessageResponse)
async def update_settings(
    body: SettingsUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    """Update one or more settings. Only keys in CONFIGURABLE_SETTINGS are accepted."""
    repo = SettingsRepo(db)
    updated = 0

    for key, value in body.settings.items():
        if key not in CONFIGURABLE_SETTINGS:
            raise HTTPException(400, f"Unknown setting: {key}")

        # Skip masked values (user didn't change the secret)
        if _is_masked(value):
            continue

        meta = CONFIGURABLE_SETTINGS[key]
        await repo.set(key, value, is_secret=meta.is_secret)
        settings.update_override(key, value)
        updated += 1

    return MessageResponse(message=f"Updated {updated} setting(s)")


@router.delete("/{key}", response_model=MessageResponse)
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    """Remove a DB override, reverting to the environment variable value."""
    if key not in CONFIGURABLE_SETTINGS:
        raise HTTPException(400, f"Unknown setting: {key}")

    repo = SettingsRepo(db)
    await repo.delete(key)
    settings.update_override(key, "")

    return MessageResponse(message=f"Setting '{key}' reverted to environment default")
