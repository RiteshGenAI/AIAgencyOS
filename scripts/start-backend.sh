#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f "$ROOT/backend/.env" ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' "$ROOT/backend/.env" | xargs)
fi
export PYTHONPATH="$ROOT"
cd "$ROOT/backend"
./.venv/bin/python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
