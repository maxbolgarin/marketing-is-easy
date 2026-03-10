"""Channel endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.deps import get_db
from src.api.schemas.channel import ChannelResponse, ChannelUpdateRequest
from src.api.schemas.common import MessageResponse
from src.db.models import ApiUser, PlatformAccount

router = APIRouter()


@router.get("", response_model=list[ChannelResponse])
async def list_channels(
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    result = await db.execute(select(PlatformAccount).order_by(PlatformAccount.platform))
    return [ChannelResponse.model_validate(a) for a in result.scalars().all()]


@router.patch("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: uuid.UUID,
    body: ChannelUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    account = await db.get(PlatformAccount, channel_id)
    if not account:
        raise HTTPException(status_code=404, detail="Channel not found")
    if body.account_name is not None:
        account.account_name = body.account_name
    if body.config is not None:
        account.config = body.config
    if body.is_active is not None:
        account.is_active = body.is_active
    await db.commit()
    await db.refresh(account)
    return ChannelResponse.model_validate(account)


@router.post("/{channel_id}/test", response_model=MessageResponse)
async def test_channel(
    channel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    account = await db.get(PlatformAccount, channel_id)
    if not account:
        raise HTTPException(status_code=404, detail="Channel not found")
    # Basic connectivity check — verify credentials exist
    if not account.credentials:
        return MessageResponse(message="No credentials configured")
    return MessageResponse(message=f"Channel {account.platform} is configured")
