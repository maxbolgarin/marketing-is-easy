from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import AppSetting


class SettingsRepo:
    """Repository for reading and writing runtime-configurable app settings."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> dict[str, str]:
        """Return all settings as a key->value mapping."""
        result = await self._session.execute(select(AppSetting))
        rows = result.scalars().all()
        return {row.key: row.value for row in rows}

    async def get(self, key: str) -> str | None:
        """Return the value for a single key, or None if not found."""
        result = await self._session.execute(
            select(AppSetting.value).where(AppSetting.key == key)
        )
        return result.scalar_one_or_none()

    async def set(self, key: str, value: str, is_secret: bool = False) -> None:
        """Upsert a setting using PostgreSQL INSERT ... ON CONFLICT DO UPDATE."""
        stmt = (
            insert(AppSetting)
            .values(key=key, value=value, is_secret=is_secret)
            .on_conflict_do_update(
                index_elements=[AppSetting.key],
                set_={
                    "value": value,
                    "is_secret": is_secret,
                    "updated_at": func.now(),
                },
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def set_many(self, items: dict[str, str]) -> None:
        """Upsert multiple settings. Each call goes through set() for consistent upsert logic."""
        for key, value in items.items():
            await self.set(key, value)

    async def delete(self, key: str) -> None:
        """Delete a setting row by key."""
        await self._session.execute(delete(AppSetting).where(AppSetting.key == key))
        await self._session.commit()
