def test_customer_dashboard_includes_visual_stage_content(client, seeded_users):
    customer = seeded_users["customer"]

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

    body = response.get_data(as_text=True)
    assert "Platform Command Center" in body
    assert "Train Smarter. Coach Faster. Operate with Confidence." in body
    assert "dashboard-visual.js" in body
