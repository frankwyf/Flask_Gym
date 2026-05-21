"""Initialize database tables for local development."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app, db, bcrypt
from app.public_catalog import bootstrap_public_catalog


def main() -> None:
    with app.app_context():
        db.create_all()
        bootstrap_public_catalog(app, db, bcrypt)
    print("Database tables are ready.")


if __name__ == "__main__":
    main()
