"""ARQ worker entrypoint.

Run with:
    uv run arq app.jobs.worker.WorkerSettings
"""

from __future__ import annotations

import logging

from arq.connections import RedisSettings

from app.core.config import settings
from app.jobs.tasks.attio_sync import attio_sync_client, attio_sync_lead
from app.jobs.tasks.lead_enrichment import lead_enrichment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("operra.worker")


async def startup(ctx: dict) -> None:
    logger.info("ARQ worker starting (env=%s)", settings.environment)


async def shutdown(ctx: dict) -> None:
    logger.info("ARQ worker shutting down")


class WorkerSettings:
    functions = [lead_enrichment, attio_sync_lead, attio_sync_client]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 60
