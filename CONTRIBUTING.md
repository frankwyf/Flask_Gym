# Contributing Guide

Thanks for considering a contribution to Flask Gym.

## Development Setup

1. Create and activate virtual environment.
2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Configure local environment:

```powershell
Copy-Item configs/env.example .env
```

4. Initialize local database:

```powershell
python scripts/db_create.py
```

## Run Tests

```powershell
python -m pytest -q
```

## Pull Request Checklist

- Keep changes focused and small.
- Add or update tests for behavior changes.
- Update docs when commands, config, or structure changes.
- Ensure all tests pass locally.

## Commit Style

Conventional-style commit messages are preferred, for example:

- `feat: add course search endpoint`
- `fix: prevent anonymous access to manager route`
- `docs: update setup steps`
