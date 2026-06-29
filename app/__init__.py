import logging
import os
import time
import uuid
import warnings
from logging.handlers import RotatingFileHandler

from app.errors.handlers import errors
from config import Config
from flask import Flask, g, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config.from_object(Config)

warnings.simplefilter("ignore")


def apply_runtime_hardening(flask_app):
    default_secret = "dev-only-secret-change-in-production"

    if flask_app.config.get("USE_PROXY_FIX"):
        flask_app.wsgi_app = ProxyFix(
            flask_app.wsgi_app,
            x_for=flask_app.config.get("PROXY_FIX_X_FOR", 1),
            x_proto=flask_app.config.get("PROXY_FIX_X_PROTO", 1),
            x_host=flask_app.config.get("PROXY_FIX_X_HOST", 1),
            x_port=flask_app.config.get("PROXY_FIX_X_PORT", 1),
        )

    if flask_app.config.get("STRICT_CONFIG") and not flask_app.config.get("TESTING"):
        if flask_app.config.get("SECRET_KEY") == default_secret:
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
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

    started_at = getattr(g, "request_started_at", None)
    if started_at is not None:
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        app.logger.info(
            "request_id=%s method=%s path=%s status=%s latency_ms=%.2f",
            request_id,
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
    return response


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
