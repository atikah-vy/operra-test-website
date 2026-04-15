"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

logger = logging.getLogger("operra.api")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Operra API starting (env=%s)", settings.environment)
    yield
    logger.info("Operra API shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Operra STL OS API",
        version="0.1.0",
        description="Business Operating System — leads, clients, billing, bookings, social, automations.",
        lifespan=lifespan,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz", tags=["system"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    _register_routers(app)
    return app


def _register_routers(app: FastAPI) -> None:
    # Resource routers
    from app.routers import (
        analytics,
        automations,
        bookings,
        clients,
        invoices,
        leads,
        social,
    )
    from app.routers.webhooks import attio as wh_attio
    from app.routers.webhooks import calcom as wh_calcom
    from app.routers.webhooks import clerk as wh_clerk
    from app.routers.webhooks import meta as wh_meta

    prefix = settings.api_prefix
    app.include_router(leads.router, prefix=prefix)
    app.include_router(leads.public_router, prefix=prefix)
    app.include_router(clients.router, prefix=prefix)
    app.include_router(invoices.router, prefix=prefix)
    app.include_router(bookings.router, prefix=prefix)
    app.include_router(social.router, prefix=prefix)
    app.include_router(automations.router, prefix=prefix)
    app.include_router(analytics.router, prefix=prefix)

    # Webhook routers
    app.include_router(wh_clerk.router, prefix=prefix)
    app.include_router(wh_attio.router, prefix=prefix)
    app.include_router(wh_calcom.router, prefix=prefix)
    app.include_router(wh_meta.router, prefix=prefix)


app = create_app()
