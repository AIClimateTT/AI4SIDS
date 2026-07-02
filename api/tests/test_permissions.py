import pytest

from tests.factories import login, make_org, make_user


@pytest.fixture()
def guarded_app(app):
    """Attach sample guarded routes to the test app."""
    from fastapi import Depends

    from app.core.auth import CurrentUser
    from app.core.permissions import (
        ROLE_ORG_ADMIN,
        require_org_access,
        require_role,
    )

    @app.get("/admin-only", dependencies=[Depends(require_role())])
    def admin_only():
        return {"ok": True}

    @app.get(
        "/org-admin-up",
        dependencies=[Depends(require_role(ROLE_ORG_ADMIN))],
    )
    def org_admin_up():
        return {"ok": True}

    @app.get("/orgs/{org_id}/ping")
    def org_ping(org_id: int, current_user: CurrentUser):
        require_org_access(org_id, current_user)
        return {"ok": True}

    return app


def test_member_denied_super_admin_route(guarded_app, client, db):
    make_user(db, "m@x.org", role="member")
    headers = login(client, "m@x.org")
    assert client.get("/admin-only", headers=headers).status_code == 403


def test_super_admin_passes_everything(guarded_app, client, db):
    make_user(db, "root@x.org", role="super_admin")
    headers = login(client, "root@x.org")
    assert client.get("/admin-only", headers=headers).status_code == 200
    assert client.get("/org-admin-up", headers=headers).status_code == 200
    assert client.get("/orgs/999/ping", headers=headers).status_code == 200


def test_org_admin_passes_role_but_not_other_org(guarded_app, client, db):
    org = make_org(db, name="Met Office")
    other = make_org(db, name="Water Authority")
    make_user(db, "oa@met.org", role="org_admin", org_id=org.id)
    headers = login(client, "oa@met.org")
    assert client.get("/org-admin-up", headers=headers).status_code == 200
    assert client.get("/admin-only", headers=headers).status_code == 403
    assert client.get(f"/orgs/{org.id}/ping", headers=headers).status_code == 200
    assert client.get(f"/orgs/{other.id}/ping", headers=headers).status_code == 403


def test_unauthenticated_gets_401(guarded_app, client):
    assert client.get("/admin-only").status_code == 401
