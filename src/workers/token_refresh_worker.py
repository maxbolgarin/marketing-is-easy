"""Background worker for OAuth token refresh.

Checks platform_accounts for tokens expiring within 10 days and refreshes them.

Run: python -m src.workers.token_refresh_worker
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select

from src.config.settings import settings
from src.db.models import PlatformAccount, async_session, engine, Base
from src.publishing.token_manager import refresh_instagram_long_lived_token, token_expiry_from_response

log = structlog.get_logger()

REFRESH_WINDOW_DAYS = 10
CHECK_INTERVAL_S = 3600  # check every hour


async def refresh_expiring_tokens() -> None:
    """Find tokens expiring soon and refresh them."""
    threshold = datetime.now(timezone.utc) + timedelta(days=REFRESH_WINDOW_DAYS)

    async with async_session() as session:
        stmt = (
            select(PlatformAccount)
            .where(PlatformAccount.is_active == True)
            .where(PlatformAccount.token_expires_at <= threshold)
        )
        result = await session.execute(stmt)
        accounts = list(result.scalars().all())

    if not accounts:
        log.debug("no_tokens_expiring_soon")
        return

    log.info("refreshing_tokens", count=len(accounts))

    for account in accounts:
        try:
            if account.platform == "instagram_post" or account.platform == "instagram":
                access_token = account.credentials.get("access_token", "")
                if not access_token:
                    log.warning("no_access_token", account_id=str(account.id))
                    continue

                data = await refresh_instagram_long_lived_token(access_token)
                new_expiry = token_expiry_from_response(data)

                async with async_session() as session:
                    acc = await session.get(PlatformAccount, account.id)
                    if acc:
                        acc.credentials = {**acc.credentials, "access_token": data["access_token"]}
                        acc.token_expires_at = new_expiry
                        await session.commit()

                log.info(
                    "token_refreshed",
                    account_id=str(account.id),
                    platform=account.platform,
                    new_expiry=new_expiry.isoformat(),
                )

        except Exception as e:
            log.error(
                "token_refresh_failed",
                account_id=str(account.id),
                platform=account.platform,
                error=str(e),
            )
            # Notify admin
            try:
                from aiogram import Bot
                bot = Bot(token=settings.tg_bot_token)
                await bot.send_message(
                    settings.tg_admin_chat_id,
                    f"⚠️ <b>Token refresh failed</b>\n"
                    f"Platform: {account.platform}\n"
                    f"Account: {account.account_name or str(account.id)[:8]}\n"
                    f"Error: {e}",
                    parse_mode="HTML",
                )
                await bot.session.close()
            except Exception:
                pass


async def main():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    log.info("token_refresh_worker_started", check_interval_hours=CHECK_INTERVAL_S // 3600)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        while True:
            await refresh_expiring_tokens()
            await asyncio.sleep(CHECK_INTERVAL_S)
    except asyncio.CancelledError:
        log.info("token_refresh_worker_stopping")


if __name__ == "__main__":
    asyncio.run(main())
