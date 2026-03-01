#!/bin/bash
# Reset database and load seed data in the backend container.
# Usage: fixtures.sh [--migrations]
#   --migrations: use Alembic migrations instead of create_all to create tables

set -e
cd "$(dirname "$0")/../.."

USE_MIGRATIONS=false
for arg in "$@"; do
    case "$arg" in
        --migrations) USE_MIGRATIONS=true ;;
    esac
done

SERVICE="backend"

run_in_container() {
    if docker compose ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
        docker compose exec "$SERVICE" "$@"
    else
        docker compose run --rm "$SERVICE" "$@"
    fi
}

if [ "$USE_MIGRATIONS" = true ]; then
    run_in_container python -m app.console database fixtures --migrations
else
    run_in_container python -m app.console database fixtures
fi
