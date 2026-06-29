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

### Changed

- Repository structure documentation updated to match current layout.
- CI workflow upgraded to a multi-stage CI/CD pipeline with quality gate,
  Python matrix testing, artifact publishing, and container build packaging.
- Default security-oriented Flask session configuration hardening.
- CI workflow hardened with least-privilege permissions, concurrency control, and stricter Bandit gate.
- GitHub Actions major versions updated (`checkout@v5`, `setup-python@v6`, `upload-artifact@v5`) to remove Node 20 runtime deprecation warnings.
- Anonymous-route guard logic refactored into maintainable allowlist constants.
