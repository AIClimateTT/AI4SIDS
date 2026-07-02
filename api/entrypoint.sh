#!/bin/sh
# Container entrypoint: apply database migrations, then start the API.
#
# There are currently no Alembic revisions (schema comes from create_all +
# migrate_schema at app startup), so `alembic upgrade head` is a no-op today.
# It runs here so that once revisions are added, staging picks them up on
# every deploy without a separate migration step.
set -e

echo "Running database migrations (alembic upgrade head)..."
alembic upgrade head

exec uvicorn app:app --host 0.0.0.0 --port "${PORT:-8080}"
