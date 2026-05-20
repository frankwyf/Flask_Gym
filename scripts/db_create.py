"""Initialize database tables for local development."""

from app import app, db


def main() -> None:
    with app.app_context():
        db.create_all()
    print("Database tables are ready.")


if __name__ == "__main__":
    main()
