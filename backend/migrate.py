"""Apply incremental database migrations manually."""

from backend.app.db.init_db import _run_migrations


def main() -> None:
    _run_migrations()
    print("Migrations applied.")


if __name__ == "__main__":
    main()
