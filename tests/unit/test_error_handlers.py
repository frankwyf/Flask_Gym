from pathlib import Path

from flask import Flask, abort

from app.errors.handlers import errors


def test_error_handlers_render_expected_status_codes():
    template_dir = Path(__file__).resolve().parents[2] / "app" / "templates"
    error_app = Flask(__name__, template_folder=str(template_dir))
    error_app.register_blueprint(errors)

    @error_app.route("/_abort_403")
    def abort_403():
        abort(403)

    @error_app.route("/_abort_404")
    def abort_404():
        abort(404)

    @error_app.route("/_abort_429")
    def abort_429():
        abort(429)

    @error_app.route("/_abort_500")
    def abort_500():
        abort(500)

    @error_app.route("/_abort_502")
    def abort_502():
        abort(502)

    @error_app.route("/_abort_503")
    def abort_503():
        abort(503)

    @error_app.route("/_abort_504")
    def abort_504():
        abort(504)

    with error_app.test_client() as test_client:
        assert test_client.get("/_abort_403").status_code == 403
        assert test_client.get("/_abort_404").status_code == 404
        assert test_client.get("/_abort_429").status_code == 429
        assert test_client.get("/_abort_500").status_code == 500
        assert test_client.get("/_abort_502").status_code == 502
        assert test_client.get("/_abort_503").status_code == 503
        assert test_client.get("/_abort_504").status_code == 504
