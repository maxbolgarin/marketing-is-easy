"""FastAPI application — monolith entry point.

Starts the API server and launches all background services
(Telegram bot, generation worker, publish worker, video worker, token refresher)
as asyncio tasks. Services are gracefully skipped when required tokens are missing.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from src.api.auth import hash_password
from src.api.routers import assets, auth, calendar, channels, dashboard, posts, themes
from src.api.routers import settings as settings_router
from src.config.settings import settings
from src.db.models import ApiUser, Base, async_session, engine

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure structlog for the monolith process
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    # Create tables if needed (works alongside Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Load runtime settings from database
    await settings.load_from_db()
    logger.info("runtime_settings_loaded")

    # Seed default admin user if configured and not existing
    if settings.api_default_admin_password:
        async with async_session() as session:
            stmt = select(ApiUser).where(ApiUser.username == settings.api_default_admin_username)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                user = ApiUser(
                    id=uuid.uuid4(),
                    username=settings.api_default_admin_username,
                    password_hash=hash_password(settings.api_default_admin_password),
                    display_name="Admin",
                )
                session.add(user)
                await session.commit()
                logger.info("Created default admin user", username=settings.api_default_admin_username)

    # Launch background services
    background_tasks: list[asyncio.Task] = []

    # Telegram bot
    if settings.tg_bot_token:
        from src.admin_bot.bot import run as run_bot
        background_tasks.append(asyncio.create_task(run_bot(), name="telegram_bot"))
        logger.info("started_service", service="telegram_bot")
    else:
        logger.warning("skipped_service", service="telegram_bot", reason="tg_bot_token is empty")

    # Generation worker (always starts — handles missing keys per-task)
    from src.workers.generation_worker import run as run_gen_worker
    background_tasks.append(asyncio.create_task(run_gen_worker(), name="generation_worker"))
    logger.info("started_service", service="generation_worker")

    # Publish worker (needs TG token for Telegram publishing)
    if settings.tg_bot_token:
        from src.workers.publish_worker import run as run_pub_worker
        background_tasks.append(asyncio.create_task(run_pub_worker(), name="publish_worker"))
        logger.info("started_service", service="publish_worker")
    else:
        logger.warning("skipped_service", service="publish_worker", reason="tg_bot_token is empty")

    # Video worker (needs OpenAI key)
    if settings.openai_api_key:
        from src.workers.video_worker import run as run_video_worker
        background_tasks.append(asyncio.create_task(run_video_worker(), name="video_worker"))
        logger.info("started_service", service="video_worker")
    else:
        logger.warning("skipped_service", service="video_worker", reason="openai_api_key is empty")

    # Token refresh worker (always runs — handles gracefully if no accounts)
    from src.workers.token_refresh_worker import run as run_token_refresher
    background_tasks.append(asyncio.create_task(run_token_refresher(), name="token_refresher"))
    logger.info("started_service", service="token_refresher")

    app.state.background_tasks = background_tasks

    yield

    # Shutdown: cancel all background tasks
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
    logger.info("background_services_stopped")

    from src.workers.task_queue import close_redis
    await close_redis()


app = FastAPI(
    title="BioMaxing API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.api_cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static media files — create dir if needed
os.makedirs(settings.media_storage_path, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_storage_path), name="media")

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(themes.router, prefix="/api/themes", tags=["themes"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])


@app.get("/api/health")
async def health():
    services = {}
    for task in getattr(app.state, "background_tasks", []):
        services[task.get_name()] = "running" if not task.done() else "stopped"
    return {"status": "ok", "services": services}
