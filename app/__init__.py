import logging
import os
import time
import warnings
from logging.handlers import RotatingFileHandler

from app.errors.handlers import errors
from config import Config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)

warnings.simplefilter("ignore")

mail = Mail(app)

app.register_blueprint(errors)  # Blueprint for customized error pages

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # object to hash the password
migrate = Migrate(app, db)  # database migration
login_manager = LoginManager(app)  # the login manager that manager the log in session


def create_app():
    # Keep compatibility for scripts that import an app factory.
    return app


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
