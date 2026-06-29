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

## 4. Prometheus scrape example

```yaml
scrape_configs:
  - job_name: flask-gym
    metrics_path: /metrics
    static_configs:
      - targets: ["flask-gym.example.com"]
    params:
      token: ["replace-with-metrics-token"]
```

## 5. Operational recommendations

- Keep alert thresholds aligned with your real SLOs.
- Route critical alerts to on-call channels.
- Correlate alerts with `/sloz` output for quick triage.
