"""Simple Redis-based task queue for background processing."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import redis.asyncio as redis

from src.config.settings import settings

_redis: redis.Redis | None = None

QUEUE_KEY = "social:task_queue"
VIDEO_QUEUE_KEY = "social:video_queue"
PROCESSING_KEY = "social:processing"


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def enqueue_task(task_type: str, payload: dict, priority: int = 5) -> str:
    """Add a task to the queue. Returns task ID."""
    r = await get_redis()
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "type": task_type,
        "payload": payload,
        "priority": priority,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await r.lpush(QUEUE_KEY, json.dumps(task))
    return task_id


async def dequeue_task(timeout: int = 5) -> dict | None:
    """Block-pop a task from the queue. Returns task dict or None."""
    r = await get_redis()
    result = await r.brpop(QUEUE_KEY, timeout=timeout)
    if result:
        _, data = result
        return json.loads(data)
    return None


async def enqueue_video_task(payload: dict, priority: int = 3) -> str:
    """Add a video generation task to the dedicated video queue."""
    r = await get_redis()
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "type": "generate_video",
        "payload": payload,
        "priority": priority,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await r.lpush(VIDEO_QUEUE_KEY, json.dumps(task))
    return task_id


async def dequeue_video_task(timeout: int = 10) -> dict | None:
    """Block-pop a task from the video queue. Returns task dict or None."""
    r = await get_redis()
    result = await r.brpop(VIDEO_QUEUE_KEY, timeout=timeout)
    if result:
        _, data = result
        return json.loads(data)
    return None


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
