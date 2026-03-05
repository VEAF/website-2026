# VEAF Website — Deployment Guide

Deploy the VEAF website from pre-built Docker images.

## Prerequisites

- **Docker** and **Docker Compose** (v2+)
- **PostgreSQL 16** database, accessible from a Docker network
- **External reverse proxy** (e.g. [nginx-proxy](https://github.com/nginx-proxy/nginx-proxy)) on a Docker network named `webproxy`

## Network Setup

The compose file expects two external Docker networks. Create them if they don't exist:

```bash
docker network create webproxy    # reverse proxy network
docker network create database    # shared network with your PostgreSQL instance
```

Your PostgreSQL container (or host) must be attached to the `database` network so the backend can reach it.

## Getting the Deployment Files

You don't need to clone the entire repository. Use Git sparse checkout to fetch only the `deploy/` directory:

```bash
git clone --no-checkout --depth 1 https://github.com/VEAF/website-2026.git veaf-deploy
cd veaf-deploy
git sparse-checkout set deploy
git checkout
cd deploy
```

## Quick Start

```bash
# 1. Copy and edit the environment file
cp backend.env.dist backend.env
# Edit backend.env — at minimum set DATABASE_URL and JWT_SECRET

# 2. Pull images and start
docker compose pull
docker compose up -d

# 3. Run database migrations
docker compose exec backend uv run alembic upgrade head

# 4. (Optional) Load seed data
docker compose exec backend python -m app.console database fixtures
```

The application is now running. The nginx service is exposed to the `webproxy` network with `VIRTUAL_HOST` set (default: `veaf.org`). Your reverse proxy should pick it up automatically.

## Configuration

### Environment Variables

All backend configuration is in `backend.env`. See `backend.env.dist` for the full list with descriptions.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string (asyncpg) |
| `JWT_SECRET` | Yes | Secret key for JWT tokens — use a long random string |
| `APP_URL` | Yes | Public URL of the application |
| `MAIL_SERVER` | No | SMTP server for outgoing emails |
| `DISCORD_CLIENT_ID` | No | Discord OAuth2 client ID |
| `DISCORD_CLIENT_SECRET` | No | Discord OAuth2 client secret |
| `RECAPTCHA_SECRET_KEY` | No | Google reCAPTCHA v3 secret |

### Compose Variables

These can be set in a `.env` file next to `docker-compose.yml` or exported in your shell:

| Variable | Default | Description |
|---|---|---|
| `TAG` | `latest` | Docker image tag to use |
| `VIRTUAL_HOST` | `veaf.org` | Hostname for reverse proxy auto-discovery |

## Updating

```bash
# Pull the latest images
docker compose pull

# Restart services
docker compose up -d

# Apply any new database migrations
docker compose exec backend uv run alembic upgrade head
```

## Architecture

```mermaid
graph TD
    Internet -->|HTTPS| nginx-proxy["nginx-proxy<br/>(external reverse proxy)"]

    subgraph net_webproxy ["webproxy network"]
        nginx-proxy --> nginx["nginx<br/>(alpine)"]
    end

    subgraph net_default ["default network"]
        nginx -->|"/api/*"| backend["backend<br/>FastAPI"]
        nginx -->|"/*"| frontend["frontend<br/>Vue 3 + nginx"]
    end

    subgraph net_database ["database network"]
        backend --> postgres["PostgreSQL 16<br/>(external)"]
    end
```

## Troubleshooting

**Backend won't start** — Check `docker compose logs backend`. Most common issue: database not reachable. Verify `DATABASE_URL` and that the `database` network is correctly set up.

**502 Bad Gateway** — The backend may still be starting. Wait for the health check to pass: `docker compose ps` should show `healthy` status.

**Migrations fail** — Ensure the database user has CREATE/ALTER privileges on the target database.
