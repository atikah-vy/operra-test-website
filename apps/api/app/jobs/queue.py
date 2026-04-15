"""ARQ enqueue helpers.

Keeps a process-wide ARQ Redis connection for cheap `enqueue()` calls from FastAPI
request handlers. The pool is created lazily on first use.
"""

from __future__ import annotations

import logging
from typing import Any

from arq.connections import ArqRedis, RedisSettings, create_pool

from app.core.config import settings

logger = logging.getLogger("operra.jobs")

_pool: ArqRedis | None = None


def _redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(settings.redis_url)


async def get_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(_redis_settings())
    return _pool


async def enqueue(task_name: str, **kwargs: Any) -> None:
    """Enqueue a named ARQ task. Logs and swallows errors so request paths stay fast."""
    try:
        pool = await get_pool()
        await pool.enqueue_job(task_name, **kwargs)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to enqueue %s: %s", task_name, exc)


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
