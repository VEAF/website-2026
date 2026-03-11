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

## Discord SSO

Users can log in with their Discord account via OAuth2.

### Setup

1. Create an application on the [Discord Developer Portal](https://discord.com/developers/applications)
2. Under **OAuth2 > General**:
   - Copy the **Client ID** and **Client Secret**
   - Add the **Redirect URI**: `https://your-domain/auth/discord/callback` (dev: `http://veaf.localhost/auth/discord/callback`)
3. Set the environment variables in `backend/.env`:

```env
DISCORD_CLIENT_ID=123456789012345678
DISCORD_CLIENT_SECRET=your-client-secret
DISCORD_REDIRECT_URI=http://veaf.localhost/auth/discord/callback
```

The required scopes (`identify` and `email`) are requested automatically by the application.

### How it works

- If a Discord user has the same email as an existing account, the accounts are automatically linked.
- If no matching account exists, a new account is created using the Discord username.
- Users created via Discord have no local password; they must log in through Discord.

---

## Discord Bot (Voice Channels)

Display active users in Discord voice channels on the website (similar to the TeamSpeak feature).

### Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and select your application (or create one)
2. Under **Bot**:
   - Click **Reset Token** to generate a bot token, and copy it
   - Enable **Privileged Gateway Intents**: **Server Members Intent** and **Presence Intent**
3. Under **OAuth2 > URL Generator**:
   - Select the **bot** scope
   - No special permissions are needed (the bot only reads voice states)
   - Open the generated URL to invite the bot to your Discord server
4. Copy the **Guild ID** (server ID) of your Discord server: right-click the server name in Discord > **Copy Server ID** (requires Developer Mode enabled in Discord settings)
5. Set the environment variables in `backend/.env`:

```env
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_GUILD_ID=123456789012345678
```

### How it works

- The backend polls the Discord API every 5 minutes to fetch voice channel members
- Results are cached in memory (20-minute TTL) and exposed via `GET /api/discord-voice/status`
- The `/discord` page displays active voice channels with connected users
- A badge in the navigation menu shows the number of users currently in voice channels
- If `DISCORD_BOT_TOKEN` or `DISCORD_GUILD_ID` are not set, the feature is disabled

---

## Environment variables

See `backend/.env.dist` for the full list. Essential variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL (asyncpg) |
| `JWT_SECRET` | Secret key for JWT tokens |
| `APP_URL` | Public application URL |
| `UPLOAD_DIR` | Upload file storage directory |
| `DISCORD_CLIENT_ID` | Discord OAuth2 application Client ID |
| `DISCORD_CLIENT_SECRET` | Discord OAuth2 application Client Secret |
| `DISCORD_REDIRECT_URI` | Discord OAuth2 redirect URI (must match Discord Developer Portal) |
| `DISCORD_BOT_TOKEN` | Discord bot token (for voice channel display) |
| `DISCORD_GUILD_ID` | Discord server (guild) ID (for voice channel display) |
