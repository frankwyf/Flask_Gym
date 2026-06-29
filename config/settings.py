import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)


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


class Config:
    """Application configuration loaded from environment variables."""

    CSRF_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-in-production")
    DEBUG = _env_flag("DEBUG", False)
    TESTING = _env_flag("TESTING", False)
    STRICT_CONFIG = _env_flag("STRICT_CONFIG", False)
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")

    # Upload-safe defaults; override MAX_CONTENT_LENGTH_MB for larger payloads.
    MAX_CONTENT_LENGTH = _env_int("MAX_CONTENT_LENGTH_MB", 32) * 1024 * 1024

    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "flask_gym_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _env_flag("SESSION_COOKIE_SECURE", False)

    USE_PROXY_FIX = _env_flag("USE_PROXY_FIX", False)
    PROXY_FIX_X_FOR = _env_int("PROXY_FIX_X_FOR", 1)
    PROXY_FIX_X_PROTO = _env_int("PROXY_FIX_X_PROTO", 1)
    PROXY_FIX_X_HOST = _env_int("PROXY_FIX_X_HOST", 1)
    PROXY_FIX_X_PORT = _env_int("PROXY_FIX_X_PORT", 1)

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
