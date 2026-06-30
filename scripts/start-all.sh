#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== Starting AI Agency OS locally ==="
echo "Ensure PostgreSQL is running: ./scripts/start-postgres.sh"

"$ROOT/scripts/start-backend.sh" &
"$ROOT/scripts/start-frontend.sh" &
wait
