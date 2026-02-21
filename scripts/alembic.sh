#!/bin/bash
# Execute Alembic commands in the backend container.
# Uses exec if the container is running, run otherwise.
#
# Usage: ./scripts/alembic.sh [alembic arguments...]
# Examples:
#   ./scripts/alembic.sh upgrade head
#   ./scripts/alembic.sh revision --autogenerate -m "add users table"
#   ./scripts/alembic.sh downgrade -1

SERVICE="backend"

if docker compose ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
    docker compose exec "$SERVICE" uv run alembic "$@"
else
    docker compose run --rm "$SERVICE" uv run alembic "$@"
fi
