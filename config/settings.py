import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)
DEFAULT_SECRET_KEY = "dev-only-secret-change-in-production"
DEFAULT_CSP_POLICY = (
    "default-src 'self'; "
    "img-src 'self' data: https:; "
    "style-src 'self' 'unsafe-inline' https:; "
    "script-src 'self' 'unsafe-inline' https:; "
    "font-src 'self' data: https:; "
    "connect-src 'self' https:; "
    "frame-ancestors 'self'; "
    "base-uri 'self'; "
    "form-action 'self'"
)
DEFAULT_PERMISSIONS_POLICY = "geolocation=(), microphone=(), camera=()"


def _env_flag(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in ("1", "true", "yes", "on")


def _env_int(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


class Config:
    """Application configuration loaded from environment variables."""

    CSRF_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    DEBUG = _env_flag("DEBUG", False)
    TESTING = _env_flag("TESTING", False)
    STRICT_CONFIG = _env_flag("STRICT_CONFIG", False)
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")
    METRICS_NAMESPACE = os.getenv("METRICS_NAMESPACE", "flask_gym")

    # Upload-safe defaults; override MAX_CONTENT_LENGTH_MB for larger payloads.
    MAX_CONTENT_LENGTH = _env_int("MAX_CONTENT_LENGTH_MB", 32) * 1024 * 1024

    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "flask_gym_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _env_flag("SESSION_COOKIE_SECURE", False)
    ENABLE_HSTS = _env_flag("ENABLE_HSTS", False)
    HSTS_MAX_AGE = _env_int("HSTS_MAX_AGE", 31536000)
    HSTS_INCLUDE_SUBDOMAINS = _env_flag("HSTS_INCLUDE_SUBDOMAINS", True)
    HSTS_PRELOAD = _env_flag("HSTS_PRELOAD", False)
    SECURITY_HEADER_CSP = os.getenv("SECURITY_HEADER_CSP", DEFAULT_CSP_POLICY)
    PERMISSIONS_POLICY = os.getenv("PERMISSIONS_POLICY", DEFAULT_PERMISSIONS_POLICY)

    USE_PROXY_FIX = _env_flag("USE_PROXY_FIX", False)
    PROXY_FIX_X_FOR = _env_int("PROXY_FIX_X_FOR", 1)
    PROXY_FIX_X_PROTO = _env_int("PROXY_FIX_X_PROTO", 1)
    PROXY_FIX_X_HOST = _env_int("PROXY_FIX_X_HOST", 1)
    PROXY_FIX_X_PORT = _env_int("PROXY_FIX_X_PORT", 1)

    ENABLE_STRUCTURED_LOGGING = _env_flag("ENABLE_STRUCTURED_LOGGING", True)
    ERROR_LOG_SAMPLE_RATE = _env_float("ERROR_LOG_SAMPLE_RATE", 0.2)
    METRICS_ENABLED = _env_flag("METRICS_ENABLED", True)
    METRICS_TOKEN = os.getenv("METRICS_TOKEN", "")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'flask_gym.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = _env_int("MAIL_PORT", 25)
    MAIL_USE_SSL = _env_flag("MAIL_USE_SSL", False)
    MAIL_USE_TLS = _env_flag("MAIL_USE_TLS", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")
