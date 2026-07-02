def test_login_rejects_unknown_user(client):
    res = client.post(
        "/auth/token", data={"username": "nobody@example.com", "password": "x"}
    )
    assert res.status_code == 401
