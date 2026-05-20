from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(429)
def error_403(error):
    return render_template('errors/403.html'), 429


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500


@errors.app_errorhandler(502)
def error_500(error):
    return render_template('errors/500.html'), 502


@errors.app_errorhandler(503)
def error_500(error):
    return render_template('errors/500.html'), 503


@errors.app_errorhandler(504)
def error_500(error):
    return render_template('errors/500.html'), 504
