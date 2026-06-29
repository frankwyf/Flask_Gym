# TLS Deployment with Docker Compose

This guide extends the production-like compose stack with HTTPS termination in Nginx.

## 1. Prerequisites

- A built app image: `flask-gym:local`
- TLS certificate files prepared under:
  - `deploy/nginx/certs/fullchain.pem`
  - `deploy/nginx/certs/privkey.pem`

## 2. Security-focused environment settings

Ensure `.env` includes strong production values:

- `SECRET_KEY=<strong-random-value>`
- `SESSION_COOKIE_SECURE=true`
- `ENABLE_HSTS=true`
- `HSTS_PRELOAD=true` (only if your domain is ready)
- `METRICS_TOKEN=<secret-token>`

## 3. Start TLS stack

```bash
docker compose -f docker-compose.prod.tls.yml up -d
```

## 4. Validate endpoints

```bash
curl -I http://127.0.0.1
curl -k https://127.0.0.1/healthz
curl -k https://127.0.0.1/readyz
curl -k "https://127.0.0.1/sloz?token=<metrics-token>"
```

Expected:

- HTTP requests redirect to HTTPS
- HTTPS health endpoints return 200

## 5. Operational checks

- Confirm proxy headers are forwarded (`X-Forwarded-*`).
- Confirm HSTS header is present on HTTPS responses.
- Confirm session cookie is marked `Secure`.

## 6. Rollback path

If TLS rollout fails, stop TLS stack and restore non-TLS profile:

```bash
docker compose -f docker-compose.prod.tls.yml down
docker compose -f docker-compose.prod.yml up -d
```
