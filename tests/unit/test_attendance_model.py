"""Tests for the Attendance model and new model fields."""
import datetime

from app import app, db
from app.model import Attendance, Customer


def test_attendance_model_to_dict(clean_db):
    cust = Customer()
    cust.username = "attendance_user"
    cust.password = "hashed"
    cust.Email = "attend@test.com"
    cust.status = 1
    cust.log = 0
    cust.sex = 0
    cust.posts = 0
    db.session.add(cust)
    db.session.flush()

    record = Attendance()
    record.uid = cust.id
    record.check_in = datetime.datetime(2026, 6, 30, 9, 0, 0)
    record.check_out = datetime.datetime(2026, 6, 30, 10, 30, 0)
    record.date = datetime.date(2026, 6, 30)
    db.session.add(record)
    db.session.commit()

    d = record.to_dict()
    assert d["uid"] == cust.id
    assert d["duration_minutes"] == 90
    assert d["date"] == "2026-06-30"


def test_attendance_duration_none_when_no_checkout(clean_db):
    cust = Customer()
    cust.username = "attend_nocout"
    cust.password = "hashed"
    cust.Email = "nocout@test.com"
    cust.status = 1
    cust.log = 0
    cust.sex = 0
    cust.posts = 0
    db.session.add(cust)
    db.session.flush()

    record = Attendance()
    record.uid = cust.id
    record.check_in = datetime.datetime(2026, 6, 30, 9, 0, 0)
    record.date = datetime.date(2026, 6, 30)
    db.session.add(record)
    db.session.commit()

    assert record.duration_minutes is None
    d = record.to_dict()
    assert d["check_out"] is None


def test_customer_new_fields_exist(clean_db):
    cust = Customer()
    cust.username = "fieldtest"
    cust.password = "hashed"
    cust.Email = "field@test.com"
    cust.status = 1
    cust.log = 0
    cust.sex = 0
    cust.posts = 0
    cust.membership_expires_at = datetime.date(2027, 1, 1)
    db.session.add(cust)
    db.session.commit()

    loaded = Customer.query.filter_by(username="fieldtest").first()
    assert loaded.membership_expires_at == datetime.date(2027, 1, 1)
    assert loaded.created_at is not None
