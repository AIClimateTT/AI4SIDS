"""Permission matrix and guard-rail tests for the /api/orgs module."""
import pytest

from app.models import User
from tests.factories import login, make_org, make_user


@pytest.fixture()
def orgs_app(app):
    from app.features.orgs.controller import router as orgs_router

    app.include_router(orgs_router)
    return app


@pytest.fixture()
def setup(orgs_app, client, db):
    """Two orgs with an admin + member each, plus a super admin."""
    org_a = make_org(db, name="Ministry of Environment")
    org_b = make_org(db, name="National Met Office")
    make_user(db, "root@x.org", role="super_admin")
    admin_a = make_user(db, "admin@a.org", role="org_admin", org_id=org_a.id)
    make_user(db, "member@a.org", role="member", org_id=org_a.id)
    make_user(db, "admin@b.org", role="org_admin", org_id=org_b.id)
    return {
        "org_a": org_a,
        "org_b": org_b,
        "admin_a": admin_a,
        "root": login(client, "root@x.org"),
        "adminA": login(client, "admin@a.org"),
        "memberA": login(client, "member@a.org"),
    }


# ---------------------------------------------------------------------------
# Org CRUD (super_admin only)
# ---------------------------------------------------------------------------

def test_list_orgs_super_admin_only(setup, client):
    res = client.get("/api/orgs", headers=setup["root"])
    assert res.status_code == 200
    body = res.json()
    assert {o["name"] for o in body} == {
        "Ministry of Environment",
        "National Met Office",
    }
    by_name = {o["name"]: o for o in body}
    assert by_name["Ministry of Environment"]["user_count"] == 2

    assert client.get("/api/orgs", headers=setup["adminA"]).status_code == 403
    assert client.get("/api/orgs", headers=setup["memberA"]).status_code == 403


def test_create_org_and_duplicate_name(setup, client):
    res = client.post(
        "/api/orgs",
        headers=setup["root"],
        json={"name": "Water Authority", "description": "Rivers"},
    )
    assert res.status_code == 201
    assert res.json()["name"] == "Water Authority"

    dup = client.post(
        "/api/orgs", headers=setup["root"], json={"name": "Water Authority"}
    )
    assert dup.status_code == 409

    denied = client.post(
        "/api/orgs", headers=setup["adminA"], json={"name": "Nope"}
    )
    assert denied.status_code == 403


def test_patch_org(setup, client):
    org_id = setup["org_a"].id
    res = client.patch(
        f"/api/orgs/{org_id}",
        headers=setup["root"],
        json={"is_active": False, "description": "archived"},
    )
    assert res.status_code == 200
    assert res.json()["is_active"] is False

    assert (
        client.patch(
            f"/api/orgs/{org_id}", headers=setup["adminA"], json={"name": "X"}
        ).status_code
        == 403
    )
    assert (
        client.patch(
            "/api/orgs/9999", headers=setup["root"], json={"name": "X"}
        ).status_code
        == 404
    )


# ---------------------------------------------------------------------------
# Org users: list + permission matrix
# ---------------------------------------------------------------------------

def test_list_org_users_matrix(setup, client):
    org_a = setup["org_a"].id
    ok = client.get(f"/api/orgs/{org_a}/users", headers=setup["adminA"])
    assert ok.status_code == 200
    emails = {u["email"] for u in ok.json()}
    assert emails == {"admin@a.org", "member@a.org"}
    assert all("temp_password" not in u and "hashed_password" not in u for u in ok.json())

    assert client.get(f"/api/orgs/{org_a}/users", headers=setup["root"]).status_code == 200
    assert client.get(f"/api/orgs/{org_a}/users", headers=setup["memberA"]).status_code == 403
    org_b = setup["org_b"].id
    assert client.get(f"/api/orgs/{org_b}/users", headers=setup["adminA"]).status_code == 403


# ---------------------------------------------------------------------------
# Create user
# ---------------------------------------------------------------------------

def test_create_user_returns_temp_password_once(setup, client, db):
    org_a = setup["org_a"].id
    res = client.post(
        f"/api/orgs/{org_a}/users",
        headers=setup["adminA"],
        json={"email": "new@a.org", "full_name": "New Person", "role": "member"},
    )
    assert res.status_code == 201
    body = res.json()
    temp = body["temp_password"]
    assert len(temp) >= 10

    # temp password logs in and trips the change gate
    tok = client.post(
        "/auth/token", data={"username": "new@a.org", "password": temp}
    )
    assert tok.status_code == 200
    headers = {"Authorization": f"Bearer {tok.json()['access_token']}"}
    me = client.get("/auth/me", headers=headers).json()
    assert me["must_change_password"] is True


def test_create_user_guard_rails(setup, client, db):
    org_a = setup["org_a"].id
    # duplicate email
    dup = client.post(
        f"/api/orgs/{org_a}/users",
        headers=setup["adminA"],
        json={"email": "member@a.org", "role": "member"},
    )
    assert dup.status_code == 409
    # cannot mint super admins
    sup = client.post(
        f"/api/orgs/{org_a}/users",
        headers=setup["adminA"],
        json={"email": "evil@a.org", "role": "super_admin"},
    )
    assert sup.status_code == 422
    # inactive org refuses new users
    org = make_org(db, name="Dormant", active=False)
    res = client.post(
        f"/api/orgs/{org.id}/users",
        headers=setup["root"],
        json={"email": "x@dormant.org", "role": "member"},
    )
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Update user
# ---------------------------------------------------------------------------

def test_update_user_role_and_deactivate(setup, client, db):
    org_a = setup["org_a"].id
    member = db.query(User).filter(User.email == "member@a.org").one()
    res = client.patch(
        f"/api/orgs/{org_a}/users/{member.id}",
        headers=setup["adminA"],
        json={"role": "org_admin"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "org_admin"

    res = client.patch(
        f"/api/orgs/{org_a}/users/{member.id}",
        headers=setup["root"],
        json={"is_active": False},
    )
    assert res.status_code == 200
    assert res.json()["is_active"] is False


def test_update_user_guard_rails(setup, client, db):
    org_a = setup["org_a"].id
    admin_a = setup["admin_a"]
    member = db.query(User).filter(User.email == "member@a.org").one()

    # self-modification blocked
    self_mod = client.patch(
        f"/api/orgs/{org_a}/users/{admin_a.id}",
        headers=setup["adminA"],
        json={"is_active": False},
    )
    assert self_mod.status_code == 400

    # cannot promote to super_admin
    promote = client.patch(
        f"/api/orgs/{org_a}/users/{member.id}",
        headers=setup["adminA"],
        json={"role": "super_admin"},
    )
    assert promote.status_code == 422

    # cross-org user id -> 404
    admin_b = db.query(User).filter(User.email == "admin@b.org").one()
    cross = client.patch(
        f"/api/orgs/{org_a}/users/{admin_b.id}",
        headers=setup["root"],
        json={"role": "member"},
    )
    assert cross.status_code == 404


# ---------------------------------------------------------------------------
# Reset password
# ---------------------------------------------------------------------------

def test_reset_password_flow(setup, client, db):
    org_a = setup["org_a"].id
    member = db.query(User).filter(User.email == "member@a.org").one()
    res = client.post(
        f"/api/orgs/{org_a}/users/{member.id}/reset-password",
        headers=setup["adminA"],
    )
    assert res.status_code == 200
    temp = res.json()["temp_password"]

    tok = client.post(
        "/auth/token", data={"username": "member@a.org", "password": temp}
    )
    assert tok.status_code == 200

    # self-reset blocked
    admin_a = setup["admin_a"]
    self_reset = client.post(
        f"/api/orgs/{org_a}/users/{admin_a.id}/reset-password",
        headers=setup["adminA"],
    )
    assert self_reset.status_code == 400
