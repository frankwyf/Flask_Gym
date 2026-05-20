from datetime import datetime

import pytest

from app import app, bcrypt, db
from app.model import Coach, Customer, Health, Manager


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = Manager()
        admin.username = "Admin"
        admin.password = bcrypt.generate_password_hash("AdminPass66").decode("utf-8")
        admin.Email = "admin@example.com"
        admin.log = 0

        manager = Manager()
        manager.username = "click_manager"
        manager.password = bcrypt.generate_password_hash("ManagerPass66").decode("utf-8")
        manager.Email = "manager@example.com"
        manager.log = 0

        coach = Coach()
        coach.username = "click_coach"
        coach.password = bcrypt.generate_password_hash("CoachPass66").decode("utf-8")
        coach.cprofile = "../static/coachProfile/default_none.jpg"
        coach.Email = "coach@example.com"
        coach.speciality = "all"
        coach.sex = 0

        customer = Customer()
        customer.username = "click_customer"
        customer.password = bcrypt.generate_password_hash("CustomerPass66").decode("utf-8")
        customer.profile = "../static/customerProfile/default_none.jpg"
        customer.Email = "customer@example.com"
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
        health.aim_weight = 63
        health.prefer = "all"

        db.session.add(health)
        db.session.commit()

    with app.test_client() as test_client:
        yield test_client


def test_guest_click_navigation(client):
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200

    response = client.get("/register", follow_redirects=True)
    assert response.status_code == 200

    response = client.get("/Showdata", follow_redirects=True)
    assert response.status_code == 200


def test_customer_click_login_and_pages(client):
    response = client.post(
        "/CustomerLogin",
        data={
            "name": "click_customer",
            "psw": "CustomerPass66",
            "type": "customer",
            "remember": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with client.session_transaction() as session_data:
        session_data["role"] = "customer"

    response = client.get("/ShowAllCourse", follow_redirects=True)
    assert response.status_code == 200

    response = client.get("/ShowMycourseInpage", follow_redirects=True)
    assert response.status_code == 200


def test_coach_and_manager_click_login_flow(client):
    response = client.post(
        "/CustomerLogin",
        data={
            "name": "click_coach",
            "psw": "CoachPass66",
            "type": "coach",
            "remember": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.get("/ShowCoachcourse", follow_redirects=True)
    assert response.status_code == 200

    response = client.get("/logout?role=coach&user=click_coach", follow_redirects=True)
    assert response.status_code == 200

    response = client.post(
        "/Managers",
        data={
            "name": "click_manager",
            "psw": "ManagerPass66",
            "remember": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.get("/Showdata", follow_redirects=True)
    assert response.status_code == 200
