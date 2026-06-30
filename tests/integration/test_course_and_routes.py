"""Integration tests covering course management and additional route paths."""
import datetime

from app import app, bcrypt, db
from app.model import Coach, Connect, Course, Customer, Health


class TestCourseManagement:
    def _create_course(self, coach_cid):
        course = Course()
        course.cid = coach_cid
        course.name = "Strength 101"
        course.description = "Beginner strength training"
        course.start = datetime.datetime(2027, 3, 1, 10, 0)
        course.end = datetime.datetime(2027, 3, 1, 11, 0)
        db.session.add(course)
        db.session.commit()
        return course

    def test_show_all_course_customer(self, client, seeded_users):
        self._create_course(seeded_users["coach"].cid)

        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/ShowAllCourse")
        assert resp.status_code == 200

    def test_show_all_course_non_customer_blocked(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/ShowAllCourse")
        assert resp.status_code == 200
        assert b"Only gym customers" in resp.data

    def test_join_course(self, client, seeded_users):
        course = self._create_course(seeded_users["coach"].cid)

        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.post("/JoinCourse", data={
            "operator": seeded_users["customer"].id,
            "target": seeded_users["coach"].cid,
            "choose": course.id,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert Connect.query.filter_by(
            id=seeded_users["customer"].id, courseid=course.id
        ).first() is not None

    def test_join_course_duplicate(self, client, seeded_users):
        course = self._create_course(seeded_users["coach"].cid)

        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        client.post("/JoinCourse", data={
            "operator": seeded_users["customer"].id,
            "target": seeded_users["coach"].cid,
            "choose": course.id,
        }, follow_redirects=True)

        # Try joining again
        resp = client.post("/JoinCourse", data={
            "operator": seeded_users["customer"].id,
            "target": seeded_users["coach"].cid,
            "choose": course.id,
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Should not duplicate
        count = Connect.query.filter_by(
            id=seeded_users["customer"].id, courseid=course.id
        ).count()
        assert count == 1

    def test_cancel_course(self, client, seeded_users):
        course = self._create_course(seeded_users["coach"].cid)

        # Join first
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        client.post("/JoinCourse", data={
            "operator": seeded_users["customer"].id,
            "target": seeded_users["coach"].cid,
            "choose": course.id,
        }, follow_redirects=True)

        # Now cancel
        resp = client.get(f"/CancelCourse?operator={seeded_users['customer'].id}&target={course.id}",
                          follow_redirects=True)
        assert resp.status_code == 200
        assert Connect.query.filter_by(
            id=seeded_users["customer"].id, courseid=course.id
        ).first() is None

    def test_show_coach_course(self, client, seeded_users):
        self._create_course(seeded_users["coach"].cid)

        with client.session_transaction() as sess:
            sess["role"] = "Coach"
            sess["_user_id"] = str(seeded_users["coach"].cid)

        resp = client.get("/ShowCoachcourse")
        assert resp.status_code == 200

    def test_show_coach_course_non_coach(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/ShowCoachcourse")
        assert resp.status_code == 200
        assert b"Only Coach" in resp.data


class TestHealthzReadyz:
    def test_healthz(self, client, seeded_users):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_readyz(self, client, seeded_users):
        resp = client.get("/readyz")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ready"


class TestPublicRoutes:
    def test_index_page(self, client, seeded_users):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_unauthenticated_redirect(self, client, clean_db):
        resp = client.get("/ShowAllCourse")
        assert resp.status_code == 302  # redirect to login
