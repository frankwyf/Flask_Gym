def test_healthz_endpoint_returns_ok(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_readyz_endpoint_returns_ready(client):
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ready"


def test_response_contains_security_and_trace_headers(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("X-Permitted-Cross-Domain-Policies") == "none"
    assert response.headers.get("Content-Security-Policy")
    assert response.headers.get("Permissions-Policy")
    assert response.headers.get("X-Request-ID")


def test_metrics_endpoint_exposes_prometheus_payload(client):
    client.get("/")
    response = client.get("/metrics")

    assert response.status_code == 200
    payload = response.get_data(as_text=True)
    assert "# HELP flask_gym_requests_total" in payload
    assert "flask_gym_requests_total" in payload
    assert "# HELP flask_gym_request_latency_seconds_bucket" in payload
    assert 'le="+Inf"' in payload
    assert "# HELP flask_gym_slo_error_rate" in payload
    assert "# HELP flask_gym_slo_latency_compliance_ratio" in payload


def test_metrics_endpoint_requires_token_when_configured(client):
    from app import app

    previous_token = app.config.get("METRICS_TOKEN")
    app.config["METRICS_TOKEN"] = "metrics-token-123"
    try:
        forbidden = client.get("/metrics")
        assert forbidden.status_code == 403

        allowed = client.get("/metrics", headers={"X-Metrics-Token": "metrics-token-123"})
        assert allowed.status_code == 200
    finally:
        app.config["METRICS_TOKEN"] = previous_token


def test_metrics_endpoint_can_be_disabled(client):
    from app import app

    previous_state = app.config.get("METRICS_ENABLED", True)
    app.config["METRICS_ENABLED"] = False
    try:
        response = client.get("/metrics")
        assert response.status_code == 404
    finally:
        app.config["METRICS_ENABLED"] = previous_state


def test_sloz_endpoint_returns_slo_snapshot(client):
    client.get("/")
    response = client.get("/sloz")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert "slo" in payload
    assert "error_rate" in payload["slo"]
    assert "latency_compliance_ratio" in payload["slo"]


def test_sloz_endpoint_requires_token_when_configured(client):
    from app import app

    previous_token = app.config.get("METRICS_TOKEN")
    app.config["METRICS_TOKEN"] = "metrics-token-123"
    try:
        forbidden = client.get("/sloz")
        assert forbidden.status_code == 403

        allowed = client.get("/sloz", headers={"X-Metrics-Token": "metrics-token-123"})
        assert allowed.status_code == 200
    finally:
        app.config["METRICS_TOKEN"] = previous_token


def test_hsts_header_on_secure_requests_when_enabled(client):
    from app import app

    previous_hsts_enabled = app.config.get("ENABLE_HSTS")
    previous_hsts_preload = app.config.get("HSTS_PRELOAD")

    app.config["ENABLE_HSTS"] = True
    app.config["HSTS_PRELOAD"] = True
    try:
        response = client.get("/", base_url="https://localhost")
        assert response.status_code == 200
        assert "max-age=" in response.headers.get("Strict-Transport-Security", "")
        assert "includeSubDomains" in response.headers.get("Strict-Transport-Security", "")
        assert "preload" in response.headers.get("Strict-Transport-Security", "")
    finally:
        app.config["ENABLE_HSTS"] = previous_hsts_enabled
        app.config["HSTS_PRELOAD"] = previous_hsts_preload
