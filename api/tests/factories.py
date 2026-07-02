from app.core.auth import hash_password
from app.models import Organization, User


def make_org(db, name="Ministry of Environment", active=True):
    org = Organization(name=name, is_active=active)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def make_user(
    db,
    email,
    password="pass1234",
    role="member",
    org_id=None,
    must_change_password=False,
):
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        org_id=org_id,
        must_change_password=must_change_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(client, email, password="pass1234"):
    """Log in and return Authorization headers."""
    res = client.post("/auth/token", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
