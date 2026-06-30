"""Seed local database with demo tenant, client, project, and admin user."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.seed_for_run import seed  # noqa: E402


if __name__ == "__main__":
    seed()
    print("Local seed complete.")
