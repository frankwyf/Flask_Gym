from datetime import datetime

from app import db
from app.model import Course


def test_guarded_api_routes_redirect_when_anonymous(client):
	response = client.get("/Showdata", follow_redirects=False)
	assert response.status_code == 302

	response = client.get("/addMember", follow_redirects=False)
	assert response.status_code == 302


def test_manager_api_routes_are_available_with_manager_session(client, seeded_users):
	manager = seeded_users["manager"]

	response = client.post(
		"/Managers",
		data={
			"name": manager.username,
			"psw": "ManagerPass66",
			"remember": "on",
		},
		follow_redirects=False,
	)
	assert response.status_code == 200

	with client.session_transaction() as session_data:
		session_data["role"] = "Manager"

	response = client.get("/Showdata", follow_redirects=False)
	assert response.status_code == 200

	response = client.get("/addCoach", follow_redirects=False)
	assert response.status_code == 200


def test_customer_api_login_and_join_course_flow(client, seeded_users):
	coach = seeded_users["coach"]
	customer = seeded_users["customer"]

	course = Course()
	course.cid = coach.cid
	course.name = "Strength Basics"
	course.description = "Introductory strength training"
	course.courseProfile = "../static/Course/cover/default_none.jpg"
	course.start = datetime(2026, 1, 1, 9, 0, 0)
	course.end = datetime(2026, 1, 1, 10, 0, 0)
	course.video = ""
	db.session.add(course)
	db.session.commit()

	response = client.post(
		"/CustomerLogin",
		data={
			"name": customer.username,
			"psw": "CustomerPass66",
			"type": "customer",
			"remember": "on",
		},
		follow_redirects=False,
	)
	assert response.status_code == 200

	with client.session_transaction() as session_data:
		session_data["role"] = "customer"

	response = client.post(
		"/JoinCourse",
		data={"operator": customer.id, "target": coach.cid, "choose": course.id},
		follow_redirects=False,
	)
	assert response.status_code == 302

	response = client.get("/ShowAllCourse", follow_redirects=False)
	assert response.status_code == 200

	response = client.get("/ShowMycourseInpage", follow_redirects=False)
	assert response.status_code == 200