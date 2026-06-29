import logging
import os
import hmac
import json
import secrets
import threading
import time
import uuid
import warnings
from logging.handlers import RotatingFileHandler

from app.errors.handlers import errors
from config import Config
from config.settings import DEFAULT_SECRET_KEY
from flask import Flask, Response, g, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config.from_object(Config)

warnings.simplefilter("ignore")

_PROCESS_STARTED_AT = time.time()
_METRICS_LOCK = threading.Lock()
_REQUEST_COUNT_METRICS = {}
_REQUEST_LATENCY_METRICS = {}
_REQUEST_LATENCY_HISTOGRAM = {}
_EXCEPTIONS_TOTAL = 0
_SYSTEM_RANDOM = secrets.SystemRandom()


def _latency_buckets():
    configured = app.config.get(
        "METRICS_HISTOGRAM_BUCKETS",
        (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    )
    buckets = []
    for raw in configured:
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if value > 0:
            buckets.append(value)
    return sorted(set(buckets))


def _normalize_metric_path_label():
    if request.url_rule and request.url_rule.rule:
        return request.url_rule.rule
    return request.path or "unknown"


def _prometheus_escape(value):
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _metric_name(suffix):
    namespace = app.config.get("METRICS_NAMESPACE", "flask_gym")
    normalized = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in namespace)
    normalized = normalized.strip("_") or "flask_gym"
    return f"{normalized}_{suffix}"


def _record_request_metrics(method, path_label, status_code, latency_seconds):
    with _METRICS_LOCK:
        key = (method, path_label, str(status_code))
        _REQUEST_COUNT_METRICS[key] = _REQUEST_COUNT_METRICS.get(key, 0) + 1

        latency_key = (method, path_label)
        metrics = _REQUEST_LATENCY_METRICS.setdefault(latency_key, {"sum": 0.0, "count": 0})
        metrics["sum"] += latency_seconds
        metrics["count"] += 1

        histogram = _REQUEST_LATENCY_HISTOGRAM.setdefault(
            latency_key,
            {
                "bucket_counts": {},
                "count": 0,
            },
        )
        for bound in _latency_buckets():
            histogram["bucket_counts"].setdefault(bound, 0)
            if latency_seconds <= bound:
                histogram["bucket_counts"][bound] += 1
        histogram["count"] += 1


def _record_exception_metric():
    global _EXCEPTIONS_TOTAL
    with _METRICS_LOCK:
        _EXCEPTIONS_TOTAL += 1


def render_metrics_payload():
    with _METRICS_LOCK:
        request_counts = dict(_REQUEST_COUNT_METRICS)
        request_latencies = {k: dict(v) for k, v in _REQUEST_LATENCY_METRICS.items()}
        latency_histogram = {
            k: {
                "bucket_counts": dict(v.get("bucket_counts", {})),
                "count": int(v.get("count", 0)),
            }
            for k, v in _REQUEST_LATENCY_HISTOGRAM.items()
        }
        exceptions_total = _EXCEPTIONS_TOTAL

    requests_total_metric = _metric_name("requests_total")
    latency_sum_metric = _metric_name("request_latency_seconds_sum")
    latency_count_metric = _metric_name("request_latency_seconds_count")
    latency_bucket_metric = _metric_name("request_latency_seconds_bucket")
    exceptions_total_metric = _metric_name("exceptions_total")
    uptime_seconds_metric = _metric_name("uptime_seconds")

    lines = [
        f"# HELP {requests_total_metric} Total HTTP requests handled by Flask Gym.",
        f"# TYPE {requests_total_metric} counter",
    ]
    for (method, path_label, status), value in sorted(request_counts.items()):
        lines.append(
            "%s{method=\"%s\",path=\"%s\",status=\"%s\"} %s"
            % (
                requests_total_metric,
                _prometheus_escape(method),
                _prometheus_escape(path_label),
                _prometheus_escape(status),
                value,
            )
        )

    lines.extend(
        [
            f"# HELP {latency_sum_metric} Accumulated HTTP latency in seconds.",
            f"# TYPE {latency_sum_metric} counter",
        ]
    )
    for (method, path_label), values in sorted(request_latencies.items()):
        lines.append(
            "%s{method=\"%s\",path=\"%s\"} %.6f"
            % (latency_sum_metric, _prometheus_escape(method), _prometheus_escape(path_label), values["sum"])
        )

    lines.extend(
        [
            f"# HELP {latency_bucket_metric} Histogram buckets for HTTP request latency in seconds.",
            f"# TYPE {latency_bucket_metric} histogram",
        ]
    )
    for (method, path_label), values in sorted(latency_histogram.items()):
        cumulative = 0
        for bound in _latency_buckets():
            bucket_count = int(values["bucket_counts"].get(bound, 0))
            cumulative = bucket_count
            lines.append(
                "%s{method=\"%s\",path=\"%s\",le=\"%.6g\"} %s"
                % (
                    latency_bucket_metric,
                    _prometheus_escape(method),
                    _prometheus_escape(path_label),
                    bound,
                    cumulative,
                )
            )
        lines.append(
            "%s{method=\"%s\",path=\"%s\",le=\"+Inf\"} %s"
            % (
                latency_bucket_metric,
                _prometheus_escape(method),
                _prometheus_escape(path_label),
                int(values.get("count", 0)),
            )
        )

    lines.extend(
        [
            f"# HELP {latency_count_metric} Number of latency samples collected.",
            f"# TYPE {latency_count_metric} counter",
        ]
    )
    for (method, path_label), values in sorted(request_latencies.items()):
        lines.append(
            "%s{method=\"%s\",path=\"%s\"} %s"
            % (latency_count_metric, _prometheus_escape(method), _prometheus_escape(path_label), values["count"])
        )

    lines.extend(
        [
            f"# HELP {exceptions_total_metric} Total unhandled request exceptions.",
            f"# TYPE {exceptions_total_metric} counter",
            f"{exceptions_total_metric} {exceptions_total}",
            f"# HELP {uptime_seconds_metric} Process uptime in seconds.",
            f"# TYPE {uptime_seconds_metric} gauge",
            f"{uptime_seconds_metric} {max(time.time() - _PROCESS_STARTED_AT, 0):.2f}",
        ]
    )

    return "\n".join(lines) + "\n"


def build_metrics_response():
    return Response(render_metrics_payload(), mimetype="text/plain; version=0.0.4")


def metrics_token_is_valid(provided_token):
    expected_token = app.config.get("METRICS_TOKEN", "") or ""
    if not expected_token:
        return True
    if not provided_token:
        return False
    return hmac.compare_digest(expected_token, provided_token)


def apply_runtime_hardening(flask_app):
    if flask_app.config.get("USE_PROXY_FIX"):
        flask_app.wsgi_app = ProxyFix(
            flask_app.wsgi_app,
            x_for=flask_app.config.get("PROXY_FIX_X_FOR", 1),
            x_proto=flask_app.config.get("PROXY_FIX_X_PROTO", 1),
            x_host=flask_app.config.get("PROXY_FIX_X_HOST", 1),
            x_port=flask_app.config.get("PROXY_FIX_X_PORT", 1),
        )

    if flask_app.config.get("STRICT_CONFIG") and not flask_app.config.get("TESTING"):
        if flask_app.config.get("SECRET_KEY") == DEFAULT_SECRET_KEY:
            raise RuntimeError("STRICT_CONFIG is enabled but SECRET_KEY is not set securely.")
        if not flask_app.config.get("SESSION_COOKIE_SECURE") and not flask_app.config.get("DEBUG"):
            raise RuntimeError(
                "STRICT_CONFIG is enabled but SESSION_COOKIE_SECURE is false outside debug mode."
            )


apply_runtime_hardening(app)

mail = Mail(app)

app.register_blueprint(errors)  # Blueprint for customized error pages

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # object to hash the password
migrate = Migrate(app, db)  # database migration
login_manager = LoginManager(app)  # the login manager that manager the log in session


def create_app():
    # Keep compatibility for scripts that import an app factory.
    return app


@app.before_request
def attach_request_observability_context():
    # Attach per-request diagnostics for tracing and latency measurement.
    g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    g.request_started_at = time.perf_counter()


@app.after_request
def add_operability_headers(response):
    request_id = getattr(g, "request_id", "unknown")
    response.headers["X-Request-ID"] = request_id
    if app.config.get("ENABLE_SECURITY_HEADERS", True):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")

        csp_value = app.config.get("SECURITY_HEADER_CSP", "")
        if csp_value:
            response.headers.setdefault("Content-Security-Policy", csp_value)

        permissions_policy = app.config.get("PERMISSIONS_POLICY", "")
        if permissions_policy:
            response.headers.setdefault("Permissions-Policy", permissions_policy)

        if app.config.get("ENABLE_HSTS") and request.is_secure:
            hsts_parts = [f"max-age={max(app.config.get('HSTS_MAX_AGE', 31536000), 0)}"]
            if app.config.get("HSTS_INCLUDE_SUBDOMAINS", True):
                hsts_parts.append("includeSubDomains")
            if app.config.get("HSTS_PRELOAD", False):
                hsts_parts.append("preload")
            response.headers["Strict-Transport-Security"] = "; ".join(hsts_parts)

    started_at = getattr(g, "request_started_at", None)
    if started_at is not None:
        elapsed_seconds = max(time.perf_counter() - started_at, 0)
        elapsed_ms = elapsed_seconds * 1000
        path_label = _normalize_metric_path_label()
        _record_request_metrics(request.method, path_label, response.status_code, elapsed_seconds)

        if app.config.get("ENABLE_STRUCTURED_LOGGING", True):
            event = {
                "event": "request_complete",
                "request_id": request_id,
                "method": request.method,
                "path": path_label,
                "status_code": response.status_code,
                "latency_ms": round(elapsed_ms, 2),
                "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
                "user_agent": request.user_agent.string,
            }
            app.logger.info(json.dumps(event, ensure_ascii=True, sort_keys=True))
        else:
            app.logger.info(
                "request_id=%s method=%s path=%s status=%s latency_ms=%.2f",
                request_id,
                request.method,
                request.path,
                response.status_code,
                elapsed_ms,
            )
    return response


@app.teardown_request
def capture_sampled_request_exceptions(exc):
    if exc is None:
        return None

    _record_exception_metric()

    sample_rate = app.config.get("ERROR_LOG_SAMPLE_RATE", 0.2)
    try:
        sample_rate = float(sample_rate)
    except (TypeError, ValueError):
        sample_rate = 0.0
    sample_rate = min(max(sample_rate, 0.0), 1.0)

    if _SYSTEM_RANDOM.random() <= sample_rate:
        request_id = getattr(g, "request_id", "unknown")
        path_label = _normalize_metric_path_label()
        if app.config.get("ENABLE_STRUCTURED_LOGGING", True):
            event = {
                "event": "request_exception",
                "request_id": request_id,
                "method": request.method,
                "path": path_label,
                "exception_type": type(exc).__name__,
                "message": str(exc),
            }
            app.logger.error(json.dumps(event, ensure_ascii=True, sort_keys=True), exc_info=True)
        else:
            app.logger.error(
                "request_id=%s method=%s path=%s exception=%s",
                request_id,
                request.method,
                request.path,
                type(exc).__name__,
                exc_info=True,
            )
    return None


# create the log file automatically
def make_dir(make_dir_path):
    path = make_dir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)


log_dir_name = "Loggings"
log_file_name = 'logs-' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
log_file_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir)) + os.sep + log_dir_name
make_dir(log_file_folder)
log_file_str = log_file_folder + os.sep + log_file_name

# record every logging severer than level 'Warning'
logging.basicConfig(level=logging.WARNING)
# create logging writer, specify the storing path, size of log, the maximum number of logs
file_log_handler = RotatingFileHandler(log_file_str, maxBytes=1024 * 1024, backupCount=10)
# format the log              event time    log severity   form which file  function name  which line   log message
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
# set format
file_log_handler.setFormatter(formatter)
# add the logs to the app
logging.getLogger().addHandler(file_log_handler)

from app import routes, forms
from app.public_catalog import bootstrap_public_catalog

with app.app_context():
    bootstrap_public_catalog(app, db, bcrypt)
