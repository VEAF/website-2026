# ---- Base: shared setup ----
FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd --gid 1000 worker && useradd --uid 1000 --gid worker --create-home worker

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# ---- Dev: deps only, source mounted at runtime ----
FROM base AS dev

USER worker
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---- Prod: deps + source ----
FROM base AS prod

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

RUN chown -R worker:worker /app
USER worker
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
