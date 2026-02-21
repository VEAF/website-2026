#!/bin/sh
set -e
cd "$(dirname "$0")/.."
docker compose exec backend python -m app.console "$@"
