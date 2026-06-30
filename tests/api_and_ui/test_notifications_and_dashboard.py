"""Tests for notification API and member dashboard routes."""
import datetime

from app import db
from app.model import Notification


class TestNotificationsApi:
    def test_get_notifications_empty(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/notifications")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["notifications"] == []

    def test_get_personal_notification(self, client, seeded_users):
        notif = Notification()
        notif.uid = seeded_users["customer"].id
        notif.title = "Welcome!"
        notif.body = "Welcome to the gym."
        notif.category = "info"
        db.session.add(notif)
        db.session.commit()

        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/notifications")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["title"] == "Welcome!"

    def test_get_broadcast_notification(self, client, seeded_users):
        notif = Notification()
        notif.uid = None  # broadcast
        notif.title = "Gym closed tomorrow"
        notif.body = "Annual maintenance."
        notif.category = "alert"
        db.session.add(notif)
        db.session.commit()

        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/api/v1/notifications")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["category"] == "alert"

    def test_mark_notification_read(self, client, seeded_users):
        notif = Notification()
        notif.uid = seeded_users["customer"].id
        notif.title = "Reminder"
        notif.body = "Your class starts soon."
        db.session.add(notif)
        db.session.commit()

        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.post(f"/api/v1/notifications/{notif.id}/read")
        assert resp.status_code == 200

        resp = client.get("/api/v1/notifications")
        data = resp.get_json()
        assert data["notifications"][0]["is_read"] is True

    def test_mark_nonexistent_notification(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.post("/api/v1/notifications/9999/read")
        assert resp.status_code == 404

    def test_notifications_forbidden_for_manager(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/api/v1/notifications")
        assert resp.status_code == 403


class TestMemberDashboard:
    def test_member_dashboard_accessible(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "customer"
            sess["_user_id"] = str(seeded_users["customer"].id)

        resp = client.get("/MemberDashboard")
        assert resp.status_code == 200
        assert b"member-dashboard" in resp.data

    def test_member_dashboard_forbidden_for_manager(self, client, seeded_users):
        with client.session_transaction() as sess:
            sess["role"] = "Manager"
            sess["_user_id"] = str(seeded_users["admin"].aid)

        resp = client.get("/MemberDashboard")
        assert resp.status_code == 200
        assert b"Only customers" in resp.data
