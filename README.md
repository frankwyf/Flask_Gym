# Flask Gym Platform

[![CI](https://github.com/frankwyf/Flask_Gym/actions/workflows/tests.yml/badge.svg)](https://github.com/frankwyf/Flask_Gym/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](requirements.txt)

Portfolio-ready open-source refactor of a legacy monolithic demo project.

This application is a role-based gym management platform built with Flask. It includes customer, coach, and manager workflows for account management, course publishing, and booking.

## Template Baseline

This repository can be used as a production-oriented Flask starter template.

- Ready-to-run CI/CD with quality, test matrix, and container build stages.
- Runtime health/readiness probes with request trace headers.
- Container-first deployment path with Gunicorn and Docker.
- Open-source community defaults (contributing guide, issue forms, PR template).
- Dependency update automation via Dependabot.

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
- Ops/Delivery: GitHub Actions CI/CD, Docker, Gunicorn

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

## Runtime Health and Observability

- `GET /healthz`: liveness endpoint for container/platform probes.
- `GET /readyz`: readiness endpoint with database connectivity check.
- `GET /metrics`: Prometheus-style runtime metrics endpoint (optional token guard).
- `GET /sloz`: JSON SLO status endpoint for operators (same token guard as `/metrics`).
- `X-Request-ID` response header is attached to each request.
- Security response headers are included by default:
	- `X-Content-Type-Options: nosniff`
	- `X-Frame-Options: SAMEORIGIN`
	- `Referrer-Policy: strict-origin-when-cross-origin`
	- `Content-Security-Policy` (configurable)
	- `Permissions-Policy` (configurable)

### Observability Notes

- Structured request logs are enabled by default (`ENABLE_STRUCTURED_LOGGING=true`).
- Unhandled request exceptions are sampled into error logs via `ERROR_LOG_SAMPLE_RATE`.
- Metrics endpoint can be protected using `METRICS_TOKEN` through `X-Metrics-Token` header or `?token=` query.
- Metrics naming prefix is configurable using `METRICS_NAMESPACE`.
- Request latency histogram buckets are configurable via `METRICS_HISTOGRAM_BUCKETS`.
- SLO helper series are exported: error rate and latency-compliance ratio.
- Prometheus alert rule template: [deploy/monitoring/flask-gym-alert-rules.yml](deploy/monitoring/flask-gym-alert-rules.yml)
- Monitoring guide: [docs/operations/monitoring-prometheus.md](docs/operations/monitoring-prometheus.md)
- Monitoring compose overlay: [docker-compose.monitoring.yml](docker-compose.monitoring.yml)

## Security Baseline

- CI enforces source security scan (`bandit`) and dependency vulnerability scan (`pip-audit`).
- Runtime security headers are configurable with `ENABLE_SECURITY_HEADERS`, `SECURITY_HEADER_CSP`, and `PERMISSIONS_POLICY`.
- Optional HTTPS strict transport policy via `ENABLE_HSTS` and related `HSTS_*` settings.

## UI/UX Upgrade Highlights

- New dashboard stage section with live animated metric cards.
- Bold visual direction with responsive gradients and stronger typographic hierarchy.
- Enhanced small-screen adaptability for dashboard shell and content panels.

## Docker Deployment

Build image:

```powershell
docker build -t flask-gym:local .
```

Run container:

```powershell
docker run --rm -p 8000:8000 --env SECRET_KEY=change-me flask-gym:local
```

Open: `http://127.0.0.1:8000`

Production-like compose stack (app + nginx reverse proxy):

```powershell
docker compose -f docker-compose.prod.yml up -d
```

Operational guide: [docs/operations/deploy-compose.md](docs/operations/deploy-compose.md)

TLS profile compose stack (HTTPS termination at Nginx):

```powershell
docker compose -f docker-compose.prod.tls.yml up -d
```

TLS deployment guide: [docs/operations/deploy-compose-tls.md](docs/operations/deploy-compose-tls.md)

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

Production runtime knobs:

- `STRICT_CONFIG`: when true, app startup fails if `SECRET_KEY` is default or secure cookies are disabled outside debug mode.
- `USE_PROXY_FIX`: when true, enables `ProxyFix` middleware for reverse-proxy deployments.
- `PROXY_FIX_X_FOR`, `PROXY_FIX_X_PROTO`, `PROXY_FIX_X_HOST`, `PROXY_FIX_X_PORT`: trusted proxy hop counts.
- `MAX_CONTENT_LENGTH_MB`: upload/body size cap in MB (default `32`).
- `ENABLE_SECURITY_HEADERS`: toggles security header middleware.
- `SECURITY_HEADER_CSP`: Content Security Policy value.
- `PERMISSIONS_POLICY`: browser permissions policy header value.
- `ENABLE_HSTS`, `HSTS_MAX_AGE`, `HSTS_INCLUDE_SUBDOMAINS`, `HSTS_PRELOAD`: HSTS controls for HTTPS deployments.
- `ENABLE_STRUCTURED_LOGGING`: emit structured JSON request logs.
- `ERROR_LOG_SAMPLE_RATE`: sampled exception logging ratio (`0.0`-`1.0`).
- `METRICS_ENABLED`, `METRICS_NAMESPACE`, `METRICS_TOKEN`: metrics endpoint controls.
- `METRICS_HISTOGRAM_BUCKETS`: comma-separated request-latency bucket boundaries in seconds.
- `METRICS_SLO_LATENCY_TARGET_MS`: latency target used for compliance ratio calculation.
- `METRICS_SLO_ERROR_STATUS_MIN`: minimum HTTP status counted as SLO error (default `500`).

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
- `tests/legacy`: original baseline compatibility tests
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

GitHub Actions now runs a full CI/CD pipeline on pushes and pull requests to `main`.

- Workflow file: [.github/workflows/tests.yml](.github/workflows/tests.yml)

Pipeline stages:

- `quality`: critical lint rules + Bandit scan + pip-audit dependency vulnerability scan + CycloneDX SBOM artifact generation.
- `test`: Python version matrix (`3.10`, `3.11`, `3.12`, `3.13`) with junit + coverage artifacts.
- `build-package` (main branch): Docker image build validation + deployment bundle artifact upload.

## Release and Rollback

- Release workflow: [.github/workflows/release.yml](.github/workflows/release.yml)
	- Trigger on SemVer tags (`v*`) or manually via `workflow_dispatch`.
	- Produces release bundles (`zip`, `tar.gz`) with checksum manifest and keyless Cosign signatures, then publishes GitHub Release with auto-generated notes.
	- Attaches a generated release summary markdown artifact for deployment and verification references.
- Rollback playbook: [docs/operations/rollback.md](docs/operations/rollback.md)
- Signature verification guide: [docs/operations/verify-release-signature.md](docs/operations/verify-release-signature.md)
- Strict verifier script: [scripts/release/verify_release_signatures.sh](scripts/release/verify_release_signatures.sh)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).