# Flask Gym Platform

Portfolio-ready open-source refactor of a legacy monolithic demo project.

This application is a role-based gym management platform built with Flask. It includes customer, coach, and manager workflows for account management, course publishing, and booking.

## Documentation

- English (detailed): [docs/README.en.md](docs/README.en.md)
- Chinese (中文): [docs/README.zh-CN.md](docs/README.zh-CN.md)
- Japanese (日本語): [docs/README.ja.md](docs/README.ja.md)

## Open Source Docs

- License: [LICENSE](LICENSE)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security Policy: [SECURITY.md](SECURITY.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

## Why This Repository Exists

This repository is intended for portfolio and learning purposes:

- Removed hardcoded credentials and personal information.
- Added environment-based configuration.
- Made local startup easier with SQLite default.
- Kept original project features and templates for demonstration.

## Tech Stack

- Backend: Flask, Flask-Login, Flask-WTF, Flask-SQLAlchemy
- Data: SQLite (default), MySQL compatible via `DATABASE_URL`
- Auth/Security: Flask-Bcrypt, token-based password reset flow
- Media: Pillow, MoviePy

## Quick Start

### 1. Create virtual environment

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configure environment

Create a local environment file from template:

```powershell
Copy-Item configs/env.example .env
```

At minimum, set a strong `SECRET_KEY`.

### 4. Initialize database

```powershell
python scripts/db_create.py
```

This command now also seeds a default public catalog (coaches + free courses) so brand-new users do not land on empty pages.

### 5. Run application

```powershell
python run.py
```

Open: `http://127.0.0.1:5000`

## Default Public Catalog

Public demo coaches/courses are managed in one place: [app/public_catalog.py](app/public_catalog.py).

- `PUBLIC_MEDIA_RENAMES`: maps legacy uploaded media to clean system-facing names.
- `PUBLIC_COACHES`: default public coach identities and avatars.
- `PUBLIC_COURSES`: default free public course cards and videos.
- `bootstrap_public_catalog(...)`: idempotent bootstrap function called at app startup and during `scripts/db_create.py`.

Design goals:

- Keep seed logic out of app startup boilerplate.
- Make media naming predictable and maintainable.
- Allow safe repeated execution without duplicate rows.

## Environment Variables

Key variables:

- `SECRET_KEY`: Flask session and token signing key
- `DATABASE_URL`: SQLAlchemy database URL
	- Default: SQLite file under `instance/flask_gym.db`
	- MySQL example: `mysql+pymysql://user:password@127.0.0.1:3306/gym`
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`

See [configs/env.example](configs/env.example) for a full list.

## Security and Privacy Notes

- This repo has been sanitized for public sharing.
- Any credentials in commit history should be treated as compromised and rotated.
- Demo/sample data uses placeholder identities and emails.

## Testing

```powershell
python -m pytest
```

Run click-level integration tests only:

```powershell
python -m pytest tests/click -q
```

Test layout:

- `tests/click`: click-flow integration tests (new)
- `tests/legacy`: original coursework tests
- `tests/unit`: model/forms/error-handler unit tests
- `tests/integration`: auth and route failure-path integration tests

Core-layer coverage (excluding monolithic route file):

```powershell
python -m pytest --cov=app --cov-config=configs/.coveragerc --cov-report=term-missing -q
```

Full-project coverage (including routes):

```powershell
python -m pytest --cov=app --cov-config=configs/.coveragerc.full --cov-report=term-missing -q
```

Note: Some legacy tests may rely on specific seeded records. See language docs for troubleshooting and migration notes.

## CI

GitHub Actions runs tests automatically on pushes and pull requests to `main`.

- Workflow file: [.github/workflows/tests.yml](.github/workflows/tests.yml)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).