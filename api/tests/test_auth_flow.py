from jose import jwt

from app.core.auth import ALGORITHM, SECRET_KEY
from tests.factories import login, make_org, make_user


def test_me_returns_role_and_org(client, db):
    org = make_org(db, name="Met Office")
    make_user(db, "u@met.org", role="org_admin", org_id=org.id)
    headers = login(client, "u@met.org")
    body = client.get("/auth/me", headers=headers).json()
    assert body["role"] == "org_admin"
    assert body["org"] == {"id": org.id, "name": "Met Office"}
    assert body["must_change_password"] is False


def test_me_org_is_null_for_super_admin(client, db):
    make_user(db, "root@x.org", role="super_admin")
    headers = login(client, "root@x.org")
    body = client.get("/auth/me", headers=headers).json()
    assert body["org"] is None


def test_token_carries_role_and_org_claims(client, db):
    org = make_org(db)
    make_user(db, "u@x.org", role="member", org_id=org.id)
    res = client.post(
        "/auth/token", data={"username": "u@x.org", "password": "pass1234"}
    )
    claims = jwt.decode(
        res.json()["access_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert claims["role"] == "member"
    assert claims["org_id"] == org.id


def test_login_rejected_for_deactivated_org(client, db):
    org = make_org(db, name="Disbanded Agency", active=False)
    make_user(db, "u@old.org", org_id=org.id)
    res = client.post(
        "/auth/token", data={"username": "u@old.org", "password": "pass1234"}
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Organization is deactivated"


def test_must_change_password_gates_other_endpoints(client, db, app):
    from app.core.auth import CurrentUser

    @app.get("/protected")
    def protected(current_user: CurrentUser):
        return {"ok": True}

    make_user(db, "new@x.org", must_change_password=True)
    headers = login(client, "new@x.org")

    res = client.get("/protected", headers=headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "password_change_required"
    # /auth/me stays reachable so the frontend can see the flag
    assert client.get("/auth/me", headers=headers).status_code == 200


def test_change_password_clears_flag_and_unblocks(client, db, app):
    from app.core.auth import CurrentUser

    @app.get("/protected")
    def protected(current_user: CurrentUser):
        return {"ok": True}

    make_user(db, "new@x.org", password="temp1234", must_change_password=True)
    headers = login(client, "new@x.org", password="temp1234")

    res = client.post(
        "/auth/change-password",
        headers=headers,
        json={"current_password": "temp1234", "new_password": "brand-new-pw-9"},
    )
    assert res.status_code == 200

    headers = login(client, "new@x.org", password="brand-new-pw-9")
    assert client.get("/protected", headers=headers).status_code == 200
    assert (
        client.get("/auth/me", headers=headers).json()["must_change_password"]
        is False
    )


def test_change_password_rejects_wrong_current(client, db):
    make_user(db, "u@x.org", password="right-pw-88")
    headers = login(client, "u@x.org", password="right-pw-88")
    res = client.post(
        "/auth/change-password",
        headers=headers,
        json={"current_password": "wrong", "new_password": "whatever-99"},
    )
    assert res.status_code == 400
