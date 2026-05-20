import datetime

import pytest
from flask_login import login_user, logout_user
from wtforms.validators import ValidationError

from app import app, db
from app.forms import (
    ForgetPassword,
    ManagerAccountFrom,
    NewCourse,
    UpdateAccountFrom,
    UpdateCoachFrom,
)
from app.model import Coach, Customer, Manager


class DummyField:
    def __init__(self, data):
        self.data = data


def test_forget_password_validate_user(seeded_users):
    form = ForgetPassword()
    form.validate_user(DummyField("customer1"))

    with pytest.raises(ValidationError):
        form.validate_user(DummyField("missing-user"))


def test_update_account_validate_username_and_clean_date(seeded_users):
    current_customer = seeded_users["customer"]

    duplicate = Customer()
    duplicate.username = "dup_customer"
    duplicate.password = "x"
    duplicate.profile = "p"
    duplicate.Email = "dup@example.com"
    duplicate.status = 0
    duplicate.log = 0
    duplicate.sex = 0
    duplicate.posts = 0
    db.session.add(duplicate)
    db.session.commit()

    form = UpdateAccountFrom()

    with app.test_request_context("/"):
        login_user(current_customer)
        form.validate_username(DummyField("customer1"))
        form.validate_username(DummyField("new_customer_name"))
        with pytest.raises(ValidationError):
            form.validate_username(DummyField("dup_customer"))
        with pytest.raises(ValidationError):
            form.clean_date(datetime.date.today() + datetime.timedelta(days=1))
        logout_user()


def test_manager_and_coach_validate_username(seeded_users):
    manager_form = ManagerAccountFrom()
    coach_form = UpdateCoachFrom()

    duplicate_manager = Manager()
    duplicate_manager.username = "dup_manager"
    duplicate_manager.password = "x"
    duplicate_manager.Email = "dup_manager@example.com"
    duplicate_manager.log = 0

    duplicate_coach = Coach()
    duplicate_coach.username = "dup_coach"
    duplicate_coach.password = "x"
    duplicate_coach.cprofile = "p"
    duplicate_coach.Email = "dup_coach@example.com"
    duplicate_coach.speciality = "all"
    duplicate_coach.sex = 0

    db.session.add_all([duplicate_manager, duplicate_coach])
    db.session.commit()

    with app.test_request_context("/"):
        login_user(seeded_users["manager"])
        manager_form.validate_username(DummyField("manager2"))
        manager_form.validate_username(DummyField("manager3"))
        with pytest.raises(ValidationError):
            manager_form.validate_username(DummyField("dup_manager"))
        logout_user()

    with app.test_request_context("/"):
        login_user(seeded_users["coach"])
        coach_form.validate_username(DummyField("coach1"))
        coach_form.validate_username(DummyField("coach2"))
        with pytest.raises(ValidationError):
            coach_form.validate_username(DummyField("dup_coach"))
        logout_user()


def test_new_course_time_validator():
    form = NewCourse()
    start = datetime.datetime(2026, 1, 1, 10, 0, 0)
    end = datetime.datetime(2026, 1, 1, 9, 0, 0)

    with pytest.raises(ValidationError):
        form.validat_start_end_time(start, end)

    # Should not raise when end time is valid.
    form.validat_start_end_time(start, datetime.datetime(2026, 1, 1, 11, 0, 0))
