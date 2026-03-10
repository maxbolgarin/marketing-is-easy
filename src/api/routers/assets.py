"""Asset endpoints."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from src.api.auth import get_current_user
from src.api.schemas.asset import AssetResponse
from src.api.schemas.common import MessageResponse
from src.config.settings import settings
from src.db.models import ApiUser

router = APIRouter()


def _scan_assets(base_path: str) -> list[AssetResponse]:
    """Scan media directory for assets."""
    assets = []
    base = Path(base_path)
    if not base.exists():
        return assets
    for root, _dirs, files in os.walk(base):
        for f in files:
            if f.startswith("."):
                continue
            full = Path(root) / f
            rel = full.relative_to(base)
            assets.append(
                AssetResponse(
                    filename=f,
                    path=str(rel),
                    url=f"/media/{rel}",
                    size=full.stat().st_size,
                    modified_at=full.stat().st_mtime,
                )
            )
    return assets


@router.get("", response_model=list[AssetResponse])
async def list_assets(_user: ApiUser = Depends(get_current_user)):
    return _scan_assets(settings.media_storage_path)


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile,
    _user: ApiUser = Depends(get_current_user),
):
    from datetime import datetime

    now = datetime.now()
    upload_dir = Path(settings.media_storage_path) / settings.track / now.strftime("%Y/%m")
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    dest = upload_dir / filename
    content = await file.read()
    dest.write_bytes(content)

    rel = dest.relative_to(settings.media_storage_path)
    return AssetResponse(
        filename=filename,
        path=str(rel),
        url=f"/media/{rel}",
        size=len(content),
        modified_at=dest.stat().st_mtime,
    )


@router.delete("/{asset_path:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_path: str,
    _user: ApiUser = Depends(get_current_user),
):
    full = Path(settings.media_storage_path) / asset_path
    if not full.exists() or not full.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")
    full.unlink()
