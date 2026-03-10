"""Background worker for video generation tasks.

Runs on a dedicated Redis queue (social:video_queue) since video generation
can take 5-60 minutes and should not block text/image tasks.

Run: python -m src.workers.video_worker
"""

from __future__ import annotations

import asyncio

import structlog

from src.db.models import engine, Base
from src.workers.task_queue import dequeue_video_task, close_redis
from src.workers.generation_worker import handle_generate_video

log = structlog.get_logger()


async def run():
    """Run video worker as a background task."""
    log.info("video_worker_started")
    try:
        while True:
            task = await dequeue_video_task(timeout=10)
            if task is None:
                continue

            task_type = task.get("type")
            payload = task.get("payload", {})

            if task_type == "generate_video":
                try:
                    await handle_generate_video(payload)
                except Exception as e:
                    log.error("video_task_failed", error=str(e), exc_info=True)
            else:
                log.warning("unknown_video_task_type", task_type=task_type)
    except asyncio.CancelledError:
        log.info("video_worker_stopping")


async def main():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    log.info("video_worker_started")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await run()
    finally:
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main())
