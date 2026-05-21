from app.model import Coach, Customer


def _login_customer(client):
    return client.post(
        "/CustomerLogin",
        data={
            "name": "customer1",
            "psw": "CustomerPass66",
            "type": "customer",
            "remember": "on",
        },
        follow_redirects=True,
    )


def _login_coach(client):
    return client.post(
        "/CustomerLogin",
        data={
            "name": "coach1",
            "psw": "CoachPass66",
            "type": "coach",
            "remember": "on",
        },
        follow_redirects=True,
    )


def _login_manager(client):
    return client.post(
        "/Managers",
        data={
            "name": "manager2",
            "psw": "ManagerPass66",
            "remember": "on",
        },
        follow_redirects=True,
    )


def test_new_coach_registration_accepts_gender_scalar(client, seeded_users):
    login_response = _login_manager(client)
    assert login_response.status_code == 200

    response = client.post(
        "/newCoach",
        data={
            "name": "new_coach_scalar_gender",
            "mailenter": "new_coach_scalar_gender@example.com",
            "psw": "CoachPass66",
            "gender": "2",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    created = Coach.query.filter_by(username="new_coach_scalar_gender").first()
    assert created is not None
    assert created.sex == 2
    assert created.cprofile == "../static/coachProfile/default_female.jpg"


def test_customer_route_smoke_matrix(client, seeded_users):
    login_response = _login_customer(client)
    assert login_response.status_code == 200

    endpoints = [
        "/ShowAllCourse",
        "/ShowcourseInpage",
        "/ShowMycourseInpage",
        "/Showblog",
        "/ShowblogInpage",
        "/Showaccount",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint, follow_redirects=True)
        assert response.status_code == 200


def test_coach_route_smoke_matrix(client, seeded_users):
    login_response = _login_coach(client)
    assert login_response.status_code == 200

    endpoints = [
        "/ShowCoachcourse",
        "/ShowCoachcourseInpage",
        "/ShowStudent",
        "/ShowCoachaccount",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint, follow_redirects=True)
        assert response.status_code == 200


def test_manager_route_smoke_matrix(client, seeded_users):
    login_response = _login_manager(client)
    assert login_response.status_code == 200

    ok_or_redirect_endpoints = [
        "/Showdata",
        "/ShowCustomer",
        "/ShowManager",
        "/addCoach",
        "/addMember",
        "/addManager",
    ]
    for endpoint in ok_or_redirect_endpoints:
        response = client.get(endpoint, follow_redirects=False)
        assert response.status_code in (200, 302)


def test_public_pages_smoke(client):
    public_endpoints = [
        "/",
        "/newlogin",
        "/register",
        "/manager",
        "/ShowcourseInpage",
        "/Showblog",
        "/ShowblogInpage",
    ]
    for endpoint in public_endpoints:
        response = client.get(endpoint, follow_redirects=True)
        assert response.status_code == 200
