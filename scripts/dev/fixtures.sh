#!/bin/bash
# Reset database and load seed data in the backend container.
# Usage: fixtures.sh [args...]
#   All arguments are passed to: python -m app.console database fixtures

set -e
cd "$(dirname "$0")/../.."

SERVICE="backend"

run_in_container() {
    if docker compose ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
        docker compose exec "$SERVICE" "$@"
    else
        docker compose run --rm "$SERVICE" "$@"
    fi
}

run_in_container python -m app.console database fixtures "$@"
