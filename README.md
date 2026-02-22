# VEAF Website 2026

Community web application for the VEAF (Virtual European Air Force) for DCS World.

**Stack**: FastAPI (Python 3.12) + Vue.js 3 (TypeScript, Tailwind CSS) + PostgreSQL 16

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

---

## Production

```bash
# Copy and configure environment variables
cp backend/.env.dist backend/.env
# Edit backend/.env with your values (JWT_SECRET, DB, etc.)

# Start the application
./scripts/start.sh

# The application is available at http://veaf.localhost
```

```bash
./scripts/stop.sh      # Stop
./scripts/upgrade.sh   # Update + migrations
```

---

## Development

```bash
# Start all services (backend hot-reload, frontend Vite, PostgreSQL)
docker compose up
```

Application at `http://veaf.localhost` (Swagger: `http://veaf.localhost/api/docs`). Nginx reverse proxy routes `/api/*` to the backend and `/` to the frontend.

### Fixtures

```bash
./scripts/dev/fixtures.sh            # Reset DB + load fixtures
```

Compte admin par défaut : `mitch@localhost.dev` / `test1234`

### Python dependency management (uv)

The `scripts/uv.sh` script runs `uv` in the backend container (`exec` if the container is running, `run --rm` otherwise).

```bash
./scripts/uv.sh sync              # Install/sync dependencies
./scripts/uv.sh add httpx         # Add a dependency
./scripts/uv.sh add --group dev ruff  # Add a dev dependency
./scripts/uv.sh lock              # Regenerate the lockfile
```

### Migrations (Alembic)

The `scripts/alembic.sh` script runs Alembic in the backend container (`exec` if the container is running, `run --rm` otherwise).

```bash
./scripts/alembic.sh upgrade head
./scripts/alembic.sh revision --autogenerate -m "description"
./scripts/alembic.sh downgrade -1
```

### Tests

```bash
./scripts/uv.sh run pytest tests/ -v
docker compose exec frontend npm run test
```

### Linters

```bash
./scripts/uv.sh run ruff check .
docker compose exec frontend npm run lint
```

---

## Environment variables

See `backend/.env.dist` for the full list. Essential variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL (asyncpg) |
| `JWT_SECRET` | Secret key for JWT tokens |
| `APP_URL` | Public application URL |
| `UPLOAD_DIR` | Upload file storage directory |
