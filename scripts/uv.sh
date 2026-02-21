#!/bin/bash
# Execute uv commands in the backend container.
# Uses exec if the container is running, run otherwise.
#
# Usage: ./scripts/uv.sh [uv arguments...]
# Examples:
#   ./scripts/uv.sh sync
#   ./scripts/uv.sh add httpx
#   ./scripts/uv.sh lock

SERVICE="backend"

if docker compose ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
    docker compose exec "$SERVICE" /usr/bin/uv "$@"
else
    docker compose run --rm --no-deps "$SERVICE" /usr/bin/uv "$@"
fi
