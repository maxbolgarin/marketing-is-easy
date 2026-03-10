"""Shared FastAPI dependencies."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import async_session


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
