FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (better layer caching) — skip building the local
# package itself so hatchling doesn't complain about README.md not existing yet.
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project || uv sync --no-dev --no-install-project

# Copy full source and install the project
COPY . .
RUN uv sync --frozen --no-dev || uv sync --no-dev

EXPOSE 8000

# Default command runs the API; override to run the worker:
#   command: ["uv", "run", "arq", "app.jobs.worker.WorkerSettings"]
# Railway injects $PORT — use it if set, otherwise fall back to 8000
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
