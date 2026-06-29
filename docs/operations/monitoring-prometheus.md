# Prometheus Monitoring and Alerting

This guide shows how to consume Flask Gym metrics and wire SLO-oriented alerts.

## 1. Metrics endpoint

- Endpoint: `GET /metrics`
- Optional access token: `X-Metrics-Token` header or `?token=` query

In production, set:

- `METRICS_ENABLED=true`
- `METRICS_TOKEN=<strong-secret>`

## 2. Key metrics

- `flask_gym_requests_total`
- `flask_gym_request_latency_seconds_bucket`
- `flask_gym_slo_error_rate`
- `flask_gym_slo_latency_compliance_ratio`

Tune SLO behavior with:

- `METRICS_SLO_LATENCY_TARGET_MS`
- `METRICS_SLO_ERROR_STATUS_MIN`
- `METRICS_HISTOGRAM_BUCKETS`

## 3. Alert rule template

Use template file:

- `deploy/monitoring/flask-gym-alert-rules.yml`

It includes:

- high server error rate alert (`> 3%`)
- low latency compliance alert (`< 95%`)
- no traffic observed alert

## 4. Example config files

Included templates:

- `deploy/monitoring/prometheus.example.yml`
- `deploy/monitoring/alertmanager.example.yml`
- `deploy/monitoring/flask-gym-alert-rules.yml`

Update the metrics token and notification endpoints before using in production.

## 5. Monitoring stack (Compose overlay)

Start app stack first, then start monitoring overlay:

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml -f docker-compose.monitoring.yml up -d
```

Access:

- Prometheus: `http://127.0.0.1:9090`
- Alertmanager: `http://127.0.0.1:9093`

## 6. Prometheus scrape example

```yaml
scrape_configs:
  - job_name: flask-gym
    metrics_path: /metrics
    static_configs:
      - targets: ["flask-gym.example.com"]
    params:
      token: ["replace-with-metrics-token"]
```

## 7. Operational recommendations

- Keep alert thresholds aligned with your real SLOs.
- Route critical alerts to on-call channels.
- Correlate alerts with `/sloz` output for quick triage.
