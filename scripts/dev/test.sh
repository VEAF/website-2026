#!/bin/bash
# Run backend tests in the backend container.

set -e
cd "$(dirname "$0")/../.."

SERVICE="backend"

if docker compose ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
    docker compose exec "$SERVICE" python -m pytest tests/ -v "$@"
else
    docker compose run --rm "$SERVICE" python -m pytest tests/ -v "$@"
fi
