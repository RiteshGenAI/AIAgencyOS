#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== AI Agency OS Setup ==="

cd "$ROOT/backend"
python3 -m venv .venv 2>/dev/null || true
./.venv/bin/python -m pip install --upgrade pip -q
./.venv/bin/python -m pip install -r requirements.txt -q

cd "$ROOT/agents"
python3 -m venv .venv 2>/dev/null || true
./.venv/bin/python -m pip install --upgrade pip -q
./.venv/bin/python -m pip install -r requirements.txt -q

cd "$ROOT/frontend/app"
if command -v npm >/dev/null 2>&1; then
    npm install
else
    echo "WARNING: npm not found. Skipping frontend dependency install."
fi

[ ! -f "$ROOT/backend/.env" ] && cp "$ROOT/backend/.env.example" "$ROOT/backend/.env" && echo "Created backend/.env"
[ ! -f "$ROOT/agents/.env" ] && cp "$ROOT/agents/.env.example" "$ROOT/agents/.env" && echo "Created agents/.env"

echo "Setup complete. Run: make start-docker"
