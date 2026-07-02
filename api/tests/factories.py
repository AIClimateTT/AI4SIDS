from app.core.auth import hash_password
from app.models import User


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
