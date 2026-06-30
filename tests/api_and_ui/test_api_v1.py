"""Tests for the REST API v1 endpoints (attendance, BMI, stats)."""
import datetime

from app import app, bcrypt, db
from app.model import Attendance, Customer, Health, Manager


class TestApiStats:
    def test_stats_endpoint_requires_manager_role(self, client, seeded_users):
        # Login as customer
        with client.session_transaction() as sess:
            sess["role"] = "customer"
        from flask_login import login_user

        with app.test_request_context():
            login_user(seeded_users["customer"])

        resp = client.get("/api/v1/stats")
        assert resp.status_code in (302, 403)

    def test_stats_returns_data_for_manager(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/api/v1/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total_customers" in data
        assert "total_coaches" in data
        assert "checkins_today" in data


class TestApiBmi:
    def test_bmi_endpoint_returns_health_data(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/bmi")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "bmi" in data
        assert "bmi_category" in data
        assert "weight_kg" in data

    def test_bmi_forbidden_for_non_customer(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/api/v1/bmi")
        assert resp.status_code in (302, 403)


class TestAttendanceApi:
    def test_checkin_creates_record(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.post("/api/v1/attendance/checkin")
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "checked_in"
        assert data["record"]["uid"] == seeded_users["customer"].id

    def test_checkin_duplicate_returns_409(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        client.post("/api/v1/attendance/checkin")
        resp = client.post("/api/v1/attendance/checkin")
        assert resp.status_code == 409

    def test_checkout_completes_record(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        client.post("/api/v1/attendance/checkin")
        resp = client.post("/api/v1/attendance/checkout")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "checked_out"
        assert data["record"]["check_out"] is not None

    def test_checkout_without_checkin_returns_404(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.post("/api/v1/attendance/checkout")
        assert resp.status_code == 404

    def test_history_returns_records(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        client.post("/api/v1/attendance/checkin")
        client.post("/api/v1/attendance/checkout")

        resp = client.get("/api/v1/attendance/history")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["history"]) >= 1

    def test_attendance_forbidden_for_non_customer(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.post("/api/v1/attendance/checkin")
        assert resp.status_code in (302, 403)


class TestBmiUtility:
    def test_calc_bmi_normal(self):
        from app.routes import _calc_bmi, _bmi_category

        bmi = _calc_bmi(70, 175)
        assert bmi == 22.9
        assert _bmi_category(bmi) == "Normal"

    def test_calc_bmi_underweight(self):
        from app.routes import _calc_bmi, _bmi_category

        bmi = _calc_bmi(45, 170)
        assert _bmi_category(bmi) == "Underweight"

    def test_calc_bmi_overweight(self):
        from app.routes import _calc_bmi, _bmi_category

        bmi = _calc_bmi(85, 170)
        assert _bmi_category(bmi) == "Overweight"

    def test_calc_bmi_obese(self):
        from app.routes import _calc_bmi, _bmi_category

        bmi = _calc_bmi(110, 170)
        assert _bmi_category(bmi) == "Obese"

    def test_calc_bmi_zero_height(self):
        from app.routes import _calc_bmi, _bmi_category

        bmi = _calc_bmi(70, 0)
        assert bmi is None
        assert _bmi_category(bmi) == "unknown"


class TestApiSchedule:
    def test_schedule_returns_for_customer(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/schedule")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "schedule" in data
        assert "total" in data
        assert "page" in data

    def test_schedule_returns_for_manager(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/api/v1/schedule")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "schedule" in data

    def test_schedule_respects_pagination(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/api/v1/schedule?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["page"] == 1


class TestApiProfile:
    def test_customer_profile(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/profile")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == "customer1"
        assert data["email"] == "customer1@example.com"
        assert "bmi" in data
        assert "membership_status" in data

    def test_coach_profile(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Coach"
            sess["_user_id"] = str(seeded_users["coach"].cid)

        resp = client.get("/api/v1/profile")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == "coach1"
        assert data["speciality"] == "all"

    def test_manager_profile(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/api/v1/profile")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == "Admin"


class TestApiCourses:
    def test_courses_list_empty(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/courses")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "courses" in data
        assert data["total"] == 0

    def test_courses_list_with_data(self, client, seeded_users):
        from app import db
        from app.model import Course
        import datetime

        course = Course()
        course.cid = seeded_users["coach"].cid
        course.name = "Test Yoga"
        course.description = "A test yoga class"
        course.start = datetime.datetime(2027, 1, 10, 9, 0)
        course.end = datetime.datetime(2027, 1, 10, 10, 0)
        db.session.add(course)
        db.session.commit()

        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/courses")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 1
        assert data["courses"][0]["name"] == "Test Yoga"
