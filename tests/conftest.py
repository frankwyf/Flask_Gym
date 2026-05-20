from datetime import datetime
import warnings

import pytest

warnings.filterwarnings("ignore")

from app import app, bcrypt, db
from app.model import Coach, Customer, Health, Manager


@pytest.fixture()
def app_context():
    with app.app_context():
        yield


@pytest.fixture()
def clean_db(app_context):
    db.drop_all()
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()


@pytest.fixture()
def client(clean_db):
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def seeded_users(clean_db):
    admin = Manager()
    admin.username = "Admin"
    admin.password = bcrypt.generate_password_hash("AdminPass66").decode("utf-8")
    admin.Email = "admin@example.com"
    admin.log = 0

    manager = Manager()
    manager.username = "manager2"
    manager.password = bcrypt.generate_password_hash("ManagerPass66").decode("utf-8")
    manager.Email = "manager2@example.com"
    manager.log = 0

    coach = Coach()
    coach.username = "coach1"
    coach.password = bcrypt.generate_password_hash("CoachPass66").decode("utf-8")
    coach.cprofile = "../static/coachProfile/default_none.jpg"
    coach.Email = "coach1@example.com"
    coach.speciality = "all"
    coach.sex = 0

    customer = Customer()
    customer.username = "customer1"
    customer.password = bcrypt.generate_password_hash("CustomerPass66").decode("utf-8")
    customer.profile = "../static/customerProfile/default_none.jpg"
    customer.Email = "customer1@example.com"
    customer.status = 1
    customer.log = 0
    customer.sex = 0
    customer.posts = 0

    db.session.add_all([admin, manager, coach, customer])
    db.session.flush()

    health = Health()
    health.uid = customer.id
    health.birthday = datetime.strptime("2020-01-01", "%Y-%m-%d")
    health.height = 170
    health.weight = 65
    health.aim_weight = 62
    health.prefer = "all"
    db.session.add(health)
    db.session.commit()

    return {
        "admin": admin,
        "manager": manager,
        "coach": coach,
        "customer": customer,
        "health": health,
    }
