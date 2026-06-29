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
    assert response.headers.get("X-Request-ID")
