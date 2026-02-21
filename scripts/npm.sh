#!/bin/bash
# Execute npm commands in the frontend container.
# Uses exec if the container is running, run otherwise.
#
# Usage: ./scripts/npm.sh [npm arguments...]
# Examples:
#   ./scripts/npm.sh install
#   ./scripts/npm.sh add axios

SERVICE="frontend"

if docker compose ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
    docker compose exec "$SERVICE" npm "$@"
else
    docker compose run --rm --no-deps "$SERVICE" npm "$@"
fi
