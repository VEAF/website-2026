# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VEAF Website 2026 — community web app for the Virtual European Air Force (DCS World flight sim group). Migrated from Symfony 5.4 (source at `/home/debian/veaf/website`). UI language is **French**.

## Tech Stack

- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.0 async, PostgreSQL 16 (asyncpg), Alembic migrations
- **Frontend**: Vue 3 (Composition API) + TypeScript + Vite 6 + Tailwind CSS 3 + Pinia stores
- **Infra**: Docker Compose, Nginx reverse proxy, single uvicorn worker (for in-memory cache consistency)

## Common Commands

### Docker (primary development method)
```bash
docker compose up                    # Start all services → http://veaf.localhost
docker compose up backend            # Start backend only
scripts/dev/fixtures.sh              # Run migrations + seed data
scripts/dev/test.sh                  # Run backend tests
scripts/alembic.sh revision --autogenerate -m "description"  # Create migration
scripts/alembic.sh upgrade head      # Apply migrations
scripts/uv.sh add <package>         # Add Python dependency
scripts/npm.sh install               # Install frontend dependencies
scripts/npm.sh add <package>         # Add frontend dependency
```

### Running commands inside Docker containers

Scripts in `scripts/` use `docker compose exec` (container running) or `docker compose run --rm` (container stopped).

**Backend** (service `backend`):
- `scripts/uv.sh <args>` — run `uv` (e.g. `scripts/uv.sh add httpx`, `scripts/uv.sh sync`)
- `scripts/alembic.sh <args>` — run `uv run alembic` (e.g. `scripts/alembic.sh upgrade head`)
- `scripts/python.sh <args>` — run `python` (e.g. `scripts/python.sh -m pytest`)
- `scripts/console.sh <args>` — run `python -m app.console` (e.g. `scripts/console.sh database fixtures`)
- Direct: `docker compose exec backend <command>`

**Frontend** (service `frontend`):
- `scripts/npm.sh <args>` — run `npm` (e.g. `scripts/npm.sh install`, `scripts/npm.sh add axios`)
- Direct: `docker compose exec frontend <command>`

### Backend (without Docker)
```bash
cd backend
uv sync                              # Install dependencies
uvicorn app.main:app --reload        # Dev server on :8000
pytest                               # All tests
pytest tests/unit/                   # Unit tests only
pytest tests/integration/            # Integration tests only
pytest -k test_name                  # Single test by name
ruff check app/                      # Lint
ruff format app/                     # Format
python -m app.console database create    # Create tables
python -m app.console database fixtures  # Seed data
```

### Frontend (without Docker)
```bash
cd frontend
npm install
npm run dev                          # Dev server on :5173 (proxies /api to :8000)
npm run build                        # TypeScript check + Vite production build
npm test                             # Vitest
npm run lint                         # ESLint
```

## Architecture

### Backend (`backend/`)

**Entry point**: `app/main.py` — FastAPI app with CORS middleware, lifespan events.

**Layers**:
- `app/api/` — Route handlers. All mounted under `/api` prefix via `app/api/router.py`
- `app/auth/` — JWT tokens (`jwt.py`), password hashing (`password.py`), FastAPI dependencies (`dependencies.py`), voter-pattern permissions (`permissions.py`)
- `app/models/` — SQLAlchemy 2.0 ORM models using `mapped_column` style
- `app/schemas/` — Pydantic v2 DTOs with `from_attributes = True`
- `app/commands/` — CLI commands (Typer). Entrypoint: `app/console.py`
- `app/services/` — Business logic (to be expanded)
- `app/utils/cache.py` — In-memory TTLCache (cachetools) with async decorator
- `app/config.py` — Pydantic Settings from env vars
- `app/database.py` — Async engine, session factory, `get_db()` dependency

**Auth flow**: JWT access token (15min, Authorization header) + refresh token (7d, HttpOnly cookie). Dependencies: `get_current_user`, `get_optional_user`, `require_role`, `require_admin`.

**Key model conventions**:
- User status constants: 0=UNKNOWN, 1=CADET, 2=MEMBER, 3-8=OFFICE, 9=GUEST
- Members = status 2-8, Office = status 3-8
- Roles stored as comma-separated strings
- Use `selectinload()` for eager loading to prevent N+1

**Tests**: pytest + pytest-asyncio with SQLite in-memory DB. Fixtures in `tests/conftest.py`, factory-boy generators in `tests/factories.py`. Structure test bodies with `# GIVEN`, `# WHEN`, `# THEN` comments.

**Config**: `backend/.env` (copy from `.env.dist`). Key vars: `DATABASE_URL`, `JWT_SECRET`, `APP_URL`, `UPLOAD_DIR`.

**Pydantic schemas**: In Pydantic models, never use a mutable default value like `list` or `dict` directly. Use `default_factory=list` (via `Field(default_factory=list)`) instead.

**Ruff**: line-length=120, target Python 3.12.

**Admin paginated list pattern**: All admin list endpoints use `skip` (offset, default 0) + `limit` (default 50, max 100) query params. Total count via `select(func.count()).select_from(query.subquery())`. Response shape: `{ items: list[T], total: int }`. Frontend: `currentPage` ref + `pageSize = 50`, debounced search (300ms), `watch([search, ...filters])` resets page to 1 and reloads. Reference: `admin_users.py` / `UsersView.vue`.

### Frontend (`frontend/`)

**Entry point**: `src/main.ts` → creates Vue app with Pinia + Vue Router.

**Layers**:
- `src/api/` — Axios client (`client.ts`) with automatic JWT injection and 401 refresh. Endpoint modules: auth, users, calendar, modules, pages, servers
- `src/stores/` — Pinia Composition API stores: `auth`, `calendar`, `menu`, `servers`
- `src/composables/` — Vue composables (e.g. `useConfirm` for confirmation modals)
- `src/components/ui/` — Shared UI components (e.g. `ConfirmModal`)
- `src/router/index.ts` — 18 public routes + 9 admin routes. Guards: `requiresAuth`, `requiresAdmin` via route meta
- `src/types/` — TypeScript interfaces for API responses
- `src/views/` — Page components (public + `admin/` subfolder)
- `src/components/layout/` — AppHeader, AppFooter, NavMenu
- `src/assets/css/main.css` — Tailwind layers with custom `.btn-*`, `.input`, `.card` components

**Confirmation modals**: Use the `useConfirm()` composable which returns `confirm(msg): Promise<boolean>`. The `ConfirmModal` component is mounted once in `App.vue`. Never use native `window.confirm()`.

**Icons (FontAwesome 6 Free)**: Installed via `@fortawesome/fontawesome-free` (CSS approach). Imported globally in `main.ts` as `import '@fortawesome/fontawesome-free/css/all.min.css'`. Use `<i>` tags with FA6 long-form classes:
- Solid: `<i class="fa-solid fa-icon-name mr-1"></i>` before button text
- Brands: `<i class="fa-brands fa-discord"></i>` (or shorthand `fab`)
- Spacing: `mr-1` before text, `ml-1` after text. Sizing: use Tailwind classes (`text-xs`, `text-xl`) not FA sizing classes.
- DB menu icons are stored as CSS class strings (e.g. `"fa fa-newspaper"`, `"fab fa-discord"`). FA6 `all.min.css` includes V4/V5 shims so these work without migration.
- Do NOT use `@heroicons/vue` or inline SVG icons — use FontAwesome consistently.

**Tailwind**: Custom `veaf-*` color palette (blue gradient, primary: #5c7cfa). Config in `tailwind.config.js`.

**Vite**: `@` alias maps to `src/`. Dev proxy: `/api` → backend (via nginx at `http://veaf.localhost`).

### Infrastructure

**Docker Compose** runs 4 services: backend, frontend, nginx (reverse proxy at `http://veaf.localhost`), postgres. Nginx routes `/api/*` to backend, `/` to frontend.

**Helper scripts** in `scripts/` wrap `docker compose exec`/`run` commands. Use these instead of running commands directly in containers.

## Entity Model Reference

Original Symfony entities mapped to Python models:
- `User`/`UserModule` → `models/user.py`
- `Module`/`ModuleRole`/`ModuleSystem` → `models/module.py`
- `CalendarEvent`/`Flight`/`Slot`/`Choice`/`Vote`/`Notification` → `models/calendar.py`
- `Page`/`PageBlock`/`MenuItem`/`Url`/`File` → `models/content.py`
- `Server`/`Player`/`DcsBotSyncState` → `models/dcs.py`
- `RecruitmentEvent` → `models/recruitment.py`

Original Symfony source for reference: [VEAF website](https://github.com/VEAF/website)
