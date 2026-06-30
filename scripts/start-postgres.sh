#!/usr/bin/env bash
set -euo pipefail

CONTAINER="agency-os-postgres"
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    docker start "$CONTAINER" >/dev/null
    echo "Started existing container: $CONTAINER"
else
    docker run -d \
        --name "$CONTAINER" \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=agency_os \
        -p 5432:5432 \
        -v agency_os_postgres_data:/var/lib/postgresql/data \
        postgres:16
    echo "Created and started container: $CONTAINER"
fi
echo "PostgreSQL ready on localhost:5432"
