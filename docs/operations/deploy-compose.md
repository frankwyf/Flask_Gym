# Production-like Deployment with Docker Compose

This guide provides a production-like local deployment layout:

- Flask app container (`gunicorn`)
- Nginx reverse proxy container
- Persistent volumes for `instance/` and `Loggings/`

## 1. Prerequisites

- Docker Desktop / Docker Engine
- `.env` file created from `configs/env.example`

Recommended minimum in `.env`:

- `SECRET_KEY` set to a strong random value
- `DATABASE_URL` configured as needed

## 2. Build app image

```bash
docker build -t flask-gym:local .
```

## 3. Start stack

```bash
docker compose -f docker-compose.prod.yml up -d
```

## 4. Validate health

```bash
curl http://127.0.0.1/healthz
curl http://127.0.0.1/readyz
```

Expected:

- `/healthz` returns HTTP 200 and `{ "status": "ok" }`
- `/readyz` returns HTTP 200 when DB is reachable

## 5. Runtime operations

View logs:

```bash
docker compose -f docker-compose.prod.yml logs -f app
docker compose -f docker-compose.prod.yml logs -f nginx
```

Scale app workers (optional):

```bash
docker compose -f docker-compose.prod.yml up -d --scale app=2
```

## 6. Shutdown

```bash
docker compose -f docker-compose.prod.yml down
```

To remove volumes too:

```bash
docker compose -f docker-compose.prod.yml down -v
```

## 7. Security notes

- In real production, terminate TLS at ingress/proxy and set:
  - `SESSION_COOKIE_SECURE=true`
  - `ENABLE_HSTS=true`
- Restrict access to `/metrics` by setting `METRICS_TOKEN`.
