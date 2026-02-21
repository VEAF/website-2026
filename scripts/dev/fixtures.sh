#!/bin/bash
# Reset database and load seed data in the backend container.

set -e
cd "$(dirname "$0")/../.."

SERVICE="backend"

if docker compose ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
    docker compose exec "$SERVICE" python -m app.console database fixtures
else
    docker compose run --rm "$SERVICE" python -m app.console database fixtures
fi
