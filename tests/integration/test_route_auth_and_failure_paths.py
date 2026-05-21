from app.model import Customer, Manager


def test_customer_login_failure_paths(client, seeded_users):
    response = client.post(
        "/CustomerLogin",
        data={"name": "customer1", "psw": "wrong-pass", "type": "customer"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    response = client.post(
        "/CustomerLogin",
        data={"name": "missing", "psw": "any", "type": "customer"},
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_manager_login_failure_paths(client, seeded_users):
    response = client.get("/Managerlogin", follow_redirects=True)
    assert response.status_code == 200

    response = client.post(
        "/Managers",
        data={"name": "manager2", "psw": "wrong-pass"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    response = client.post(
        "/Managers",
        data={"name": "missing-manager", "psw": "x"},
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_reset_password_invalid_token(client):
    response = client.get("/Reset_password/not-a-valid-token", follow_redirects=False)
    assert response.status_code == 302


def test_logout_for_manager_role(client, seeded_users):
    manager = seeded_users["manager"]
    manager.log = 1
    from app import db

    db.session.commit()

    with client.session_transaction() as session_data:
        session_data["role"] = "Manager"

    response = client.get(f"/logout?role=manager&user={manager.username}", follow_redirects=False)
    assert response.status_code == 302

    refreshed = Manager.query.filter_by(username=manager.username).first()
    assert refreshed.log == 0


def test_new_account_registration_accepts_gender_scalar(client):
    response = client.post(
        "/newAccount",
        data={
            "name": "new_customer_scalar_gender",
            "mailenter": "new_customer_scalar_gender@example.com",
            "psw": "CustomerPass66",
            "gender": "1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    created = Customer.query.filter_by(username="new_customer_scalar_gender").first()
    assert created is not None
    assert created.sex == 1
    assert created.profile == "../static/customerProfile/default_male.jpg"
