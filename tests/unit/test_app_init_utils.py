from pathlib import Path

import pytest
from flask import Flask

from app import make_dir
from app import apply_runtime_hardening


def test_make_dir_creates_directory(tmp_path):
    target = tmp_path / "logs_nested"
    assert not target.exists()

    make_dir(str(target))

    assert target.exists()
    assert target.is_dir()


def test_apply_runtime_hardening_adds_proxy_fix_when_enabled():
    sample_app = Flask("proxy-test")
    original_wsgi = sample_app.wsgi_app

    sample_app.config["USE_PROXY_FIX"] = True
    sample_app.config["PROXY_FIX_X_FOR"] = 1
    sample_app.config["PROXY_FIX_X_PROTO"] = 1
    sample_app.config["PROXY_FIX_X_HOST"] = 1
    sample_app.config["PROXY_FIX_X_PORT"] = 1
    sample_app.config["STRICT_CONFIG"] = False
    sample_app.config["TESTING"] = True

    apply_runtime_hardening(sample_app)

    assert sample_app.wsgi_app is not original_wsgi
    assert sample_app.wsgi_app.__class__.__name__ == "ProxyFix"


def test_apply_runtime_hardening_raises_when_strict_and_secret_is_default():
    sample_app = Flask("strict-secret")
    sample_app.config["USE_PROXY_FIX"] = False
    sample_app.config["STRICT_CONFIG"] = True
    sample_app.config["TESTING"] = False
    sample_app.config["DEBUG"] = False
    sample_app.config["SECRET_KEY"] = "dev-only-secret-change-in-production"
    sample_app.config["SESSION_COOKIE_SECURE"] = True

    with pytest.raises(RuntimeError):
        apply_runtime_hardening(sample_app)


def test_apply_runtime_hardening_raises_when_strict_cookie_is_insecure():
    sample_app = Flask("strict-cookie")
    sample_app.config["USE_PROXY_FIX"] = False
    sample_app.config["STRICT_CONFIG"] = True
    sample_app.config["TESTING"] = False
    sample_app.config["DEBUG"] = False
    sample_app.config["SECRET_KEY"] = "really-long-non-default-secret"
    sample_app.config["SESSION_COOKIE_SECURE"] = False

    with pytest.raises(RuntimeError):
        apply_runtime_hardening(sample_app)
