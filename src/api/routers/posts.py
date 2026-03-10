"""Post endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.deps import get_db
from src.api.schemas.common import PaginatedResponse
from src.api.schemas.post import (
    ApproveRequest,
    GenerateImageRequest,
    GenerateTextRequest,
    PostCreateRequest,
    PostResponse,
    PostUpdateRequest,
    PublicationResponse,
    VariantCreateRequest,
    VariantUpdateRequest,
)
from src.db.models import ApiUser
from src.db.repo import PostRepo, PublicationRepo
from src.workers.task_queue import enqueue_task, enqueue_video_task

router = APIRouter()


def _post_response(post, publications=None) -> PostResponse:
    resp = PostResponse.model_validate(post)
    if publications:
        resp.publications = [PublicationResponse.model_validate(p) for p in publications]
    return resp


async def _post_response_with_pubs(post, db: AsyncSession) -> PostResponse:
    """Build PostResponse with publications loaded from DB."""
    pub_repo = PublicationRepo(db)
    pubs = await pub_repo.get_publications_for_post(post.id)
    return _post_response(post, pubs)


@router.get("", response_model=PaginatedResponse[PostResponse])
async def list_posts(
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    theme_id: uuid.UUID | None = None,
    platform: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    track: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    posts, total = await repo.get_posts_filtered(
        limit=limit,
        offset=offset,
        status=status_filter,
        theme_id=theme_id,
        platform=platform,
        date_from=date_from,
        date_to=date_to,
        track=track,
    )
    pub_repo = PublicationRepo(db)
    items = []
    for p in posts:
        pubs = await pub_repo.get_publications_for_post(p.id)
        items.append(_post_response(p, pubs))
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.create_post(
        track=body.track,
        language=body.language,
        text_content=body.text_content or "",
        post_type=body.post_type,
        text_prompt=body.text_prompt,
        media_type=body.media_type,
        generation_params=body.generation_params,
        status="draft",
        theme_id=body.theme_id,
        scheduled_at=body.scheduled_at,
    )
    return await _post_response_with_pubs(post, db)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return await _post_response_with_pubs(post, db)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    body: PostUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    provided = body.model_fields_set

    if "text_content" in provided:
        post.text_content = body.text_content
    if "text_prompt" in provided:
        post.text_prompt = body.text_prompt
    if "media_type" in provided:
        post.media_type = body.media_type
    if "media_urls" in provided:
        post.media_urls = body.media_urls
    if "theme_id" in provided:
        post.theme_id = body.theme_id
    if "scheduled_at" in provided:
        post.scheduled_at = body.scheduled_at
    if "status" in provided and body.status is not None:
        post.status = body.status
    if "generation_params" in provided and body.generation_params is not None:
        post.generation_params = body.generation_params

    post.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(post)

    return await _post_response_with_pubs(post, db)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await repo.update_post_status(post_id, "rejected")


# --- Post Actions ---


@router.post("/{post_id}/generate-text", response_model=PostResponse)
async def generate_text(
    post_id: uuid.UUID,
    body: GenerateTextRequest | None = None,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if body and body.prompt:
        post.text_prompt = body.prompt
        await db.commit()
    if body and body.model:
        await repo.update_post_generation_params(post_id, {"text_model": body.model})

    await repo.update_post_status(post_id, "draft")
    await enqueue_task("regenerate_post", {"post_id": str(post_id)})
    post = await repo.get_post(post_id)
    return await _post_response_with_pubs(post, db)


@router.post("/{post_id}/generate-image", response_model=PostResponse)
async def generate_image(
    post_id: uuid.UUID,
    body: GenerateImageRequest | None = None,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    media_style = body.media_style if body else "ai"
    await repo.update_post_generation_params(post_id, {"media_style": media_style})
    await enqueue_task("generate_image", {"post_id": str(post_id), "media_style": media_style})
    post = await repo.get_post(post_id)
    return await _post_response_with_pubs(post, db)


@router.post("/{post_id}/generate-video", response_model=PostResponse)
async def generate_video(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await repo.update_post_status(post_id, "draft")
    await enqueue_video_task({"post_id": str(post_id)})
    post = await repo.get_post(post_id)
    return await _post_response_with_pubs(post, db)


@router.post("/{post_id}/approve", response_model=PostResponse)
async def approve_post(
    post_id: uuid.UUID,
    body: ApproveRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await repo.update_post_status(post_id, "approved", approved_by=user.username)
    if body and body.scheduled_at:
        await repo.update_post_schedule(post_id, body.scheduled_at)
    post = await repo.get_post(post_id)
    return await _post_response_with_pubs(post, db)


@router.post("/{post_id}/reject", response_model=PostResponse)
async def reject_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await repo.update_post_status(post_id, "rejected")
    post = await repo.get_post(post_id)
    return await _post_response_with_pubs(post, db)


@router.post("/{post_id}/publish-now", response_model=PostResponse)
async def publish_now(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: ApiUser = Depends(get_current_user),
):
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await repo.update_post_status(post_id, "approved", approved_by=user.username)
    await repo.update_post_schedule(post_id, datetime.now(timezone.utc))
    post = await repo.get_post(post_id)
    return await _post_response_with_pubs(post, db)


# --- Platform Variants ---


@router.get("/{post_id}/variants", response_model=list[PublicationResponse])
async def list_variants(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    pub_repo = PublicationRepo(db)
    return [
        PublicationResponse.model_validate(p)
        for p in await pub_repo.get_publications_for_post(post_id)
    ]


@router.post(
    "/{post_id}/variants",
    response_model=PublicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_variant(
    post_id: uuid.UUID,
    body: VariantCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    # Verify post exists
    repo = PostRepo(db)
    post = await repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    pub_repo = PublicationRepo(db)
    pub = await pub_repo.create_publication(
        post_id=post_id,
        platform=body.platform,
        platform_text=body.platform_text,
        platform_media_url=body.platform_media_url,
    )
    return PublicationResponse.model_validate(pub)


@router.patch("/{post_id}/variants/{variant_id}", response_model=PublicationResponse)
async def update_variant(
    post_id: uuid.UUID,
    variant_id: uuid.UUID,
    body: VariantUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: ApiUser = Depends(get_current_user),
):
    pub_repo = PublicationRepo(db)
    pub = await pub_repo.update_publication_content(
        pub_id=variant_id,
        platform_text=body.platform_text,
        platform_media_url=body.platform_media_url,
    )
    if not pub:
        raise HTTPException(status_code=404, detail="Variant not found")
    return PublicationResponse.model_validate(pub)
