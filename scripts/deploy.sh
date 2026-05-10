#!/usr/bin/env sh
set -eu

docker compose pull postgres redis nginx || true
docker compose build
docker compose run --rm app alembic upgrade head
docker compose up -d app worker beat nginx
docker compose ps

