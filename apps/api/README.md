# Operra API

FastAPI backend for Operra. Async SQLAlchemy 2.0 against Neon Postgres, Clerk-issued JWT verification, and ARQ workers for background jobs.

## Quickstart

```bash
# From apps/api
uv sync --dev
cp ../../.env.example .env
# Fill in DATABASE_URL, CLERK_*, REDIS_URL

uv run alembic upgrade head
uv run python scripts/seed.py          # optional demo data

uv run uvicorn app.main:app --reload --port 8000
# in another shell:
uv run arq app.jobs.worker.WorkerSettings
```

Open http://localhost:8000/docs for the interactive OpenAPI UI.
