#!/bin/bash
# Upgrade and rebuild
docker compose pull
docker compose up -d --build
docker compose exec backend alembic upgrade head
echo "Upgrade complete"
