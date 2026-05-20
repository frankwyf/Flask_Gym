# Flask Gym Platform - Detailed Guide (EN)

## 1. Project Overview

This is a Flask-based gym management platform with three roles:

- Customer: register, manage profile, browse/join courses.
- Coach: manage profile and publish courses.
- Manager: administrative operations and user/course management.

The project has been refactored for open-source publication:

- credentials moved to environment variables
- local startup defaults to SQLite
- personal identifiers replaced with sample placeholders

## 2. Architecture

Current structure keeps the original monolith style:

- app/__init__.py: app and extensions initialization
- app/model.py: SQLAlchemy ORM models and login user loader
- app/routes.py: request handling and role workflows
- app/forms.py: Flask-WTF forms
- app/templates: Jinja templates
- app/static: CSS/JS/images/uploads

This is intentional for portfolio readability, while preserving original feature flow.

## 3. Configuration Strategy

Configuration is centralized in config/settings.py via Config class.

Priority:

1. environment variables
2. safe local defaults

Main variables:

- SECRET_KEY
- DATABASE_URL
- MAIL_SERVER / MAIL_PORT / MAIL_* / MAIL_DEFAULT_SENDER

## 4. Local Run (Windows)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item configs/env.example .env
python scripts/db_create.py
python run.py
```

Then open http://127.0.0.1:5000

## 5. Database Notes

Default is SQLite for zero-friction local development.

If you need MySQL:

1. create a MySQL database
2. set DATABASE_URL in .env
3. run python scripts/db_create.py again

## 6. Security Changes Made

- Removed hardcoded secret key, DB credentials, mail credentials.
- Replaced hardcoded reset email sender with MAIL_DEFAULT_SENDER.
- Replaced personal emails in tests with example.com addresses.

## 7. Known Legacy Constraints

- Routes and auth checks are mostly role checks in request/session logic.
- Some test files are data-dependent and may require seeded fixtures.
- The app uses a monolithic routes module; blueprints per domain can be a future improvement.

## 8. Suggested Next Refactor (for interviews)

- Introduce application factory pattern.
- Split routes into domain blueprints.
- Add migration scripts and seed command.
- Add pytest fixtures with isolated temporary database.
- Add CI workflow (lint + tests + security checks).
