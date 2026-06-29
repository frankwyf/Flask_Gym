# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Open-source governance docs: LICENSE, CONTRIBUTING, CODE_OF_CONDUCT,
  SECURITY, and CHANGELOG.
- GitHub Actions workflow for automated test execution on push and pull request.
- Runtime health endpoints: `/healthz` and `/readyz`.
- Request-level observability headers and request tracing ID.
- Dashboard visual stage module with animated metric cards.
- Containerization assets: `Dockerfile` and `.dockerignore`.
- Integration tests for operability/security headers and upgraded dashboard surface.
- Template engineering assets: `.editorconfig`, `pyproject.toml`, and `.pre-commit-config.yaml`.
- Open source collaboration templates: PR template, issue forms, and Dependabot config.
- Runtime hardening tests for strict config and reverse-proxy middleware behavior.
- Prometheus-style metrics endpoint (`/metrics`) with optional token guard.
- Release automation workflow for SemVer tags and manual release dispatch.
- Rollback operations playbook for production incidents.
- Release workflow checksum manifest (`.sha256`) for release bundle integrity verification.
- Production-like Docker Compose deployment template with Nginx reverse proxy.
- Deployment operations guide for compose-based rollout and health validation.

### Changed

- Repository structure documentation updated to match current layout.
- CI workflow upgraded to a multi-stage CI/CD pipeline with quality gate,
  Python matrix testing, artifact publishing, and container build packaging.
- Default security-oriented Flask session configuration hardening.
- CI workflow hardened with least-privilege permissions, concurrency control, and stricter Bandit gate.
- GitHub Actions major versions updated (`checkout@v5`, `setup-python@v6`, `upload-artifact@v5`) to remove Node 20 runtime deprecation warnings.
- Anonymous-route guard logic refactored into maintainable allowlist constants.
- Added strict production config mode (`STRICT_CONFIG`) with startup guards for insecure defaults.
- Added optional reverse-proxy middleware configuration (`USE_PROXY_FIX` + trusted hop settings).
- Docker image now includes container healthcheck against `/healthz`.
- Docker runtime base image upgraded to `python:3.13-slim` for fresher security baseline.
- Response header baseline now includes configurable CSP and Permissions-Policy.
- Runtime supports sampled exception logging and structured request logs by default.
- CI quality gate now enforces dependency vulnerability scanning with `pip-audit`.
- CI quality gate now generates and uploads CycloneDX SBOM artifacts.
- Runtime metrics now expose configurable request-latency histogram buckets for stronger alerting.
