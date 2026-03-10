"""Admin Telegram Bot — entry point.

Run: python -m src.admin_bot.bot
"""

from __future__ import annotations

import asyncio
import logging

import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config.settings import settings
from src.db.models import engine, Base


async def create_tables():
    """Create all database tables (dev mode — use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def run():
    """Run Telegram bot as a background task. Skips if token is empty."""
    if not settings.tg_bot_token:
        structlog.get_logger().warning("telegram_bot_skipped", reason="TG_BOT_TOKEN is empty")
        return

    bot = Bot(token=settings.tg_bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    from src.admin_bot.handlers.generate import router as generate_router
    from src.admin_bot.handlers.review import router as review_router

    dp.include_router(generate_router)
    dp.include_router(review_router)

    log = structlog.get_logger()
    log.info("bot_polling_started")
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    except asyncio.CancelledError:
        log.info("bot_polling_cancelled")
    finally:
        await bot.session.close()
        log.info("bot_stopped")


async def main():
    # Logging
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    log = structlog.get_logger()
    log.info("starting_admin_bot", track=settings.track, language=settings.language)

    # Create tables (dev convenience)
    await create_tables()
    log.info("database_ready")

    # Bot setup
    bot = Bot(token=settings.tg_bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    from src.admin_bot.handlers.generate import router as generate_router
    from src.admin_bot.handlers.review import router as review_router

    dp.include_router(generate_router)
    dp.include_router(review_router)

    # Start polling
    log.info("bot_polling_started")
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await bot.session.close()
        log.info("bot_stopped")


if __name__ == "__main__":
    asyncio.run(main())
