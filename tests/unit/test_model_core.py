from datetime import datetime

import pytest
from flask import session

from app import app
from app.model import (
    Coach,
    Connect,
    Course,
    Customer,
    Health,
    Manager,
    Post,
    before_user,
    load_Users,
)


class DummyField:
    def __init__(self, data):
        self.data = data


def test_load_users_for_each_role(seeded_users):
    with app.test_request_context("/"):
        session["role"] = "Manager"
        loaded = load_Users(str(seeded_users["manager"].aid))
        assert isinstance(loaded, Manager)

        session["role"] = "Coach"
        loaded = load_Users(str(seeded_users["coach"].cid))
        assert isinstance(loaded, Coach)

        session["role"] = "customer"
        loaded = load_Users(str(seeded_users["customer"].id))
        assert isinstance(loaded, Customer)


def test_before_user_allows_public_paths():
    public_paths = [
        "/",
        "/newlogin",
        "/Managerlogin",
        "/Managers",
        "/CustomerLogin",
        "/static/a.css",
        "/manager",
        "/register",
        "/newAccount",
        "/Request_password_reset",
        "/Reset_password/abc",
    ]
    for path in public_paths:
        with app.test_request_context(path):
            assert before_user() is None


def test_before_user_blocks_without_role():
    with app.test_request_context("/Showdata"):
        response = before_user()
        assert response is not None
        assert response.status_code == 302
        assert response.location.endswith("/newlogin")


def test_before_user_passes_with_role():
    with app.test_request_context("/Showdata"):
        session["role"] = "Manager"
        assert before_user() is None


def test_reset_token_roundtrip_and_invalid_branches(seeded_users):
    manager = seeded_users["manager"]
    customer = seeded_users["customer"]
    coach = seeded_users["coach"]

    manager_token = manager.get_reset_token()
    assert Manager.verify_reset_token(manager_token).aid == manager.aid

    customer_token = customer.get_reset_token()
    assert Customer.verify_reset_token(customer_token).id == customer.id

    coach_token = coach.get_reset_token()
    assert Coach.verify_reset_token(coach_token).cid == coach.cid

    wrong_role_token = manager.get_reset_token(role="Coach")
    assert Manager.verify_reset_token(wrong_role_token) is None

    wrong_role_customer_token = customer.get_reset_token(role="Manager")
    assert Customer.verify_reset_token(wrong_role_customer_token) is None

    wrong_role_coach_token = coach.get_reset_token(role="Customer")
    assert Coach.verify_reset_token(wrong_role_coach_token) is None

    assert Manager.verify_reset_token("invalid-token") is None


def test_model_initializer_methods_and_properties():
    manager = Manager()
    manager.__int__("m", "m@example.com", 0, "p")
    manager.aid = 99
    assert manager.username == "m"
    assert manager.id == 99

    customer = Customer()
    customer.__int__("c", "c@example.com", 1, "p", "profile.jpg", 0, 1, 2)
    assert customer.username == "c"
    assert customer.posts == 2

    health = Health()
    birthday = datetime.strptime("2020-01-01", "%Y-%m-%d")
    health.__int__(birthday, 180, 70, 65, "all")
    assert health.height == 180
    assert health.prefer == "all"

    post = Post()
    post.__int__("photo.jpg", "desc", "tag")
    assert post.tag == "tag"

    coach = Coach()
    coach.__int__("coach", "coach@example.com", "pw", "coach.jpg", "all", 1)
    coach.cid = 88
    assert coach.username == "coach"
    assert coach.id == 88

    course = Course()
    course.__int__("course", "desc", "cover.jpg", birthday, birthday, "video.mp4")
    assert course.name == "course"
    assert course.video == "video.mp4"

    connect = Connect(1, 2, 3)
    assert connect.id == 1
    assert connect.cid == 2
    assert connect.courseid == 3
