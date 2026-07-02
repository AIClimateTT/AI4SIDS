# Tenancy + RBAC Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Multi-org foundation for AI4SIDS-Gov: `organizations` table, roles on users, DB-enforced RBAC dependencies, invite-only temp-password flow, and frontend route guards.

**Architecture:** Extend the existing JWT auth (`api/app/core/auth.py`) in place. Authorization always reads role/org from the DB row loaded by `get_current_user`, never from token claims (claims are frontend convenience only). Frontend gains a `/login` route, a `beforeLoad` guard on `/dashboard`, an `AuthUser` in context fetched from `/auth/me`, and a forced change-password gate.

**Tech Stack:** FastAPI + SQLAlchemy + python-jose/passlib (existing), pytest + TestClient (new), React 19 + TanStack Router + Vitest/RTL (existing).

**Spec:** `docs/superpowers/specs/2026-07-02-tenancy-rbac-foundation-design.md`

## Global Constraints

- Roles are exactly: `super_admin`, `org_admin`, `member`. `super_admin` passes every role check.
- `super_admin` users have `org_id = NULL`.
- No self-signup endpoint. No email sending. No refresh tokens.
- Environmental data endpoints are NOT touched — they stay shared across orgs.
- **Spec deviation (agreed rationale):** the spec says "one Alembic migration", but the repo has zero Alembic revisions and initializes schema via `Base.metadata.create_all()` in `init_db()`. Instead, Task 2 adds an idempotent `migrate_schema()` (SQLAlchemy inspector + `ALTER TABLE ADD COLUMN`) called from `init_db()`. Same outcome: existing DBs upgrade in place; fresh DBs are complete.
- Backend tests run with: `cd api && python -m pytest tests -v`
- Frontend tests run with: `cd frontend && pnpm test`
- Commit after every task. Never commit with failing tests.

---

### Task 1: Backend test infrastructure

The API has no tests directory and no pytest dependency. Set up pytest with an in-memory SQLite DB and a minimal FastAPI app containing only the auth router (do NOT use `create_app()` from `app/__init__.py` — its lifespan starts background data-generation tasks).

**Files:**
- Modify: `api/requirements.txt`
- Create: `api/tests/__init__.py` (empty)
- Create: `api/tests/conftest.py`
- Create: `api/tests/factories.py`
- Create: `api/tests/test_smoke.py`

**Interfaces:**
- Produces: pytest fixtures `engine`, `db` (Session), `app` (FastAPI with auth router + get_db override), `client` (TestClient). Factory functions `make_org(db, name=..., active=True) -> Organization` (Task 2+ only) and `make_user(db, email, password="pass1234", role="member", org_id=None, must_change_password=False) -> User`, and `login(client, email, password) -> dict auth headers`.

- [ ] **Step 1: Add test dependencies**

Append to `api/requirements.txt`:

```
pytest==8.3.4
```

Install: `cd api && pip install -r requirements.txt`

- [ ] **Step 2: Write conftest and factories**

`api/tests/conftest.py`:

```python
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import router as auth_router
from app.core.db import get_db
from app.models import Base


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db(session_factory):
    session = session_factory()
    yield session
    session.close()


@pytest.fixture()
def app(session_factory):
    app = FastAPI()
    app.include_router(auth_router)

    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture()
def client(app):
    return TestClient(app)
```

`api/tests/factories.py`:

```python
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
```

Note: `make_user` passes `role`, `org_id`, `must_change_password` — these columns do not exist until Task 2. That is fine: Task 1's smoke test does not use the factory; Task 2 makes it real. `make_org` is added in Task 2.

- [ ] **Step 3: Write smoke test**

`api/tests/test_smoke.py`:

```python
def test_login_rejects_unknown_user(client):
    res = client.post(
        "/auth/token", data={"username": "nobody@example.com", "password": "x"}
    )
    assert res.status_code == 401
```

- [ ] **Step 4: Run it**

Run: `cd api && python -m pytest tests -v`
Expected: `test_login_rejects_unknown_user PASSED`

- [ ] **Step 5: Commit**

```bash
git add api/requirements.txt api/tests
git commit -m "test(api): add pytest infrastructure with in-memory auth test app"
```

---

### Task 2: Organization model, User columns, schema upgrade

**Files:**
- Create: `api/app/models/organization.py`
- Modify: `api/app/models/user.py`
- Modify: `api/app/models/__init__.py`
- Modify: `api/app/core/db.py` (add `migrate_schema()`, call it from `init_db()`)
- Modify: `api/tests/factories.py` (add `make_org`)
- Test: `api/tests/test_schema.py`

**Interfaces:**
- Produces: `Organization` model (`id`, `name`, `description`, `is_active`, `created_at`); `User` gains `org_id: int | None`, `role: str` (default `"member"`), `full_name: str | None`, `must_change_password: bool` (default `False`), and `org` relationship. `migrate_schema()` in `app.core.db`.

- [ ] **Step 1: Write failing tests**

`api/tests/test_schema.py`:

```python
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool


def test_user_has_org_and_role_columns(db):
    from tests.factories import make_org, make_user

    org = make_org(db, name="Ministry of Environment")
    user = make_user(db, "a@moe.gov", role="org_admin", org_id=org.id)
    assert user.role == "org_admin"
    assert user.org.name == "Ministry of Environment"
    assert user.must_change_password is False


def test_migrate_schema_upgrades_legacy_users_table(monkeypatch):
    """A DB created before this feature (users table without the new
    columns) gets the columns added in place, without data loss."""
    legacy = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with legacy.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE users ("
                "id INTEGER PRIMARY KEY, "
                "email VARCHAR NOT NULL, "
                "hashed_password VARCHAR NOT NULL, "
                "is_active BOOLEAN, "
                "created_at TIMESTAMP)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO users (email, hashed_password) "
                "VALUES ('old@user.org', 'x')"
            )
        )

    import app.core.db as db_module

    monkeypatch.setattr(db_module, "engine", legacy)
    db_module.migrate_schema()
    db_module.migrate_schema()  # idempotent — second run is a no-op

    cols = {c["name"] for c in inspect(legacy).get_columns("users")}
    assert {"org_id", "role", "full_name", "must_change_password"} <= cols
    with legacy.connect() as conn:
        row = conn.execute(
            text("SELECT email, role, must_change_password FROM users")
        ).one()
    assert row.email == "old@user.org"
    assert row.role == "member"
    assert row.must_change_password in (0, False)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && python -m pytest tests/test_schema.py -v`
Expected: FAIL — `ImportError: cannot import name 'make_org'` / `AttributeError: module 'app.core.db' has no attribute 'migrate_schema'`

- [ ] **Step 3: Implement**

`api/app/models/organization.py`:

```python
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.models.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

`api/app/models/user.py` — replace the whole file:

```python
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    role = Column(String, nullable=False, default="member")
    full_name = Column(String, nullable=True)
    must_change_password = Column(Boolean, nullable=False, default=False)

    org = relationship("Organization")
```

`api/app/models/__init__.py` — add the import and export:

```python
from app.models.base import Base
from app.models.locations import Location
from app.models.river_levels import RiverLevel
from app.models.weather import Weather
from app.models.social import Social
from app.models.river_predictions import RiverPrediction
from app.models.weekforecast import WeekForecast
from app.models.user import User
from app.models.organization import Organization

__all__ = ["Base", "Location", "RiverLevel", "Weather", "Social", "RiverPrediction", "WeekForecast", "User", "Organization"]
```

`api/app/core/db.py` — add after `init_db`'s current body (`init_db` becomes create_all + migrate):

```python
def migrate_schema():
    """Idempotently add columns introduced after a DB was created.

    The project has no Alembic revisions; schema comes from create_all(),
    which never alters existing tables. This upgrades pre-existing DBs
    (SQLite and Postgres) in place.
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns("users")}
    ddl = {
        "org_id": "ALTER TABLE users ADD COLUMN org_id INTEGER REFERENCES organizations(id)",
        "role": "ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'member'",
        "full_name": "ALTER TABLE users ADD COLUMN full_name VARCHAR",
        "must_change_password": "ALTER TABLE users ADD COLUMN must_change_password BOOLEAN NOT NULL DEFAULT FALSE",
    }
    with engine.begin() as conn:
        for name, stmt in ddl.items():
            if name not in existing:
                conn.execute(text(stmt))


def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    migrate_schema()
```

(Replace the existing `init_db` — keep everything else in the file unchanged.)

`api/tests/factories.py` — add at top with the other import, and add the function:

```python
from app.models import Organization, User


def make_org(db, name="Ministry of Environment", active=True):
    org = Organization(name=name, is_active=active)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && python -m pytest tests -v`
Expected: all PASS (smoke + 2 schema tests)

- [ ] **Step 5: Commit**

```bash
git add api/app/models api/app/core/db.py api/tests
git commit -m "feat(api): add Organization model, user org/role columns, in-place schema upgrade"
```

---

### Task 3: Permission dependencies

**Files:**
- Create: `api/app/core/permissions.py`
- Test: `api/tests/test_permissions.py`

**Interfaces:**
- Consumes: `CurrentUser` from `app.core.auth`, `User` model.
- Produces: `ROLE_SUPER_ADMIN = "super_admin"`, `ROLE_ORG_ADMIN = "org_admin"`, `ROLE_MEMBER = "member"`; `require_role(*roles) -> FastAPI dependency returning User`; `require_org_access(org_id: int, current_user: User) -> None` (raises 403). Project 2's org-management endpoints will consume these.

- [ ] **Step 1: Write failing tests**

`api/tests/test_permissions.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && python -m pytest tests/test_permissions.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.core.permissions'`

- [ ] **Step 3: Implement**

`api/app/core/permissions.py`:

```python
"""Role and organization access dependencies.

Authorization always reads role/org from the DB-loaded user (via
get_current_user), never from JWT claims, so role changes and
deactivations take effect immediately.
"""
from fastapi import HTTPException, status

from app.core.auth import CurrentUser
from app.models.user import User

ROLE_SUPER_ADMIN = "super_admin"
ROLE_ORG_ADMIN = "org_admin"
ROLE_MEMBER = "member"


def require_role(*roles: str):
    """Dependency factory: allow super_admin plus any of `roles`.

    require_role() with no arguments means super_admin only.
    """

    async def dependency(current_user: CurrentUser) -> User:
        if current_user.role == ROLE_SUPER_ADMIN or current_user.role in roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role",
        )

    return dependency


def require_org_access(org_id: int, current_user: User) -> None:
    """Raise 403 unless current_user is super_admin or belongs to org_id."""
    if current_user.role == ROLE_SUPER_ADMIN:
        return
    if current_user.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this organization",
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && python -m pytest tests -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add api/app/core/permissions.py api/tests/test_permissions.py
git commit -m "feat(api): add require_role and require_org_access dependencies"
```

---

### Task 4: Auth endpoint changes (claims, org-active check, password gate, /me, change-password)

**Files:**
- Modify: `api/app/core/auth.py`
- Test: `api/tests/test_auth_flow.py`

**Interfaces:**
- Consumes: `Organization`, `User` models.
- Produces: `POST /auth/token` adds `role`/`org_id` JWT claims and rejects users of deactivated orgs (403, detail `"Organization is deactivated"`). `GET /auth/me` returns `{ id, email, full_name, role, org: { id, name } | null, must_change_password }`. `POST /auth/change-password` accepts `{ current_password, new_password }`, clears `must_change_password`. `get_current_user` raises 403 detail `"password_change_required"` on every path except `/auth/me` and `/auth/change-password` while the flag is set. The frontend (Tasks 6–8) relies on these exact shapes and detail strings.

- [ ] **Step 1: Write failing tests**

`api/tests/test_auth_flow.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && python -m pytest tests/test_auth_flow.py -v`
Expected: FAIL — `/auth/me` lacks `role`/`org` keys, claims missing, `/auth/change-password` 404, gate absent.

- [ ] **Step 3: Implement in `api/app/core/auth.py`**

Add to the imports at the top (alongside existing ones):

```python
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.organization import Organization
from app.models.user import User
```

Replace the `UserOut` schema block with:

```python
class OrgSummary(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserMe(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: str
    org: OrgSummary | None
    must_change_password: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
```

Replace `get_current_user` with (adds `request` param and the password gate):

```python
PASSWORD_GATE_EXEMPT_PATHS = ("/auth/me", "/auth/change-password")


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: SessionDep,
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise credentials_exc

    if (
        user.must_change_password
        and request.url.path not in PASSWORD_GATE_EXEMPT_PATHS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="password_change_required",
        )
    return user
```

Replace the `login` route with (org-active check + claims):

```python
@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.org_id is not None:
        org = db.get(Organization, user.org_id)
        if org is not None and not org.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization is deactivated",
            )
    token = create_access_token(
        {"sub": user.email, "role": user.role, "org_id": user.org_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=token, token_type="bearer")
```

Replace the `/me` route and add `/change-password`:

```python
@router.get("/me", response_model=UserMe)
async def get_me(current_user: CurrentUser):
    return UserMe(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        org=OrgSummary.model_validate(current_user.org) if current_user.org else None,
        must_change_password=current_user.must_change_password,
    )


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: CurrentUser,
    db: SessionDep,
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    if len(body.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters",
        )
    current_user.hashed_password = hash_password(body.new_password)
    current_user.must_change_password = False
    db.add(current_user)
    db.commit()
    return {"status": "password_changed"}
```

Everything else in the file (helpers, `seed_default_user`, `CurrentUser`) stays as is. Note `from app.models.user import User` already exists at the top — don't duplicate it.

- [ ] **Step 4: Run all backend tests**

Run: `cd api && python -m pytest tests -v`
Expected: all PASS (smoke, schema, permissions, auth flow)

- [ ] **Step 5: Commit**

```bash
git add api/app/core/auth.py api/tests/test_auth_flow.py
git commit -m "feat(api): JWT role claims, org-active login check, password-change gate, richer /auth/me"
```

---

### Task 5: Seed script and startup hook

**Files:**
- Create: `api/app/seed_auth.py`
- Modify: `api/app/core/config.py` (add `SUPERADMIN_EMAIL`, `SUPERADMIN_PASSWORD`, `SEED_DEMO_ORGS`)
- Modify: `api/app/__init__.py` (call seeds in lifespan)
- Test: `api/tests/test_seed.py`

**Interfaces:**
- Consumes: `hash_password`, `get_user_by_email` from `app.core.auth`; `Organization`, `User` models; `settings`.
- Produces: `seed_super_admin(db)` (idempotent), `seed_demo_orgs(db)` (idempotent, two orgs each with org_admin + member; admins have `must_change_password=True`). Runnable: `python -m app.seed_auth`.

- [ ] **Step 1: Write failing tests**

`api/tests/test_seed.py`:

```python
from app.models import Organization, User


def test_seed_super_admin_idempotent(db):
    from app.seed_auth import seed_super_admin

    seed_super_admin(db)
    seed_super_admin(db)
    admins = db.query(User).filter(User.role == "super_admin").all()
    assert len(admins) == 1
    assert admins[0].org_id is None


def test_seed_demo_orgs_idempotent(db):
    from app.seed_auth import seed_demo_orgs

    seed_demo_orgs(db)
    seed_demo_orgs(db)
    assert db.query(Organization).count() == 2
    org_admins = db.query(User).filter(User.role == "org_admin").all()
    members = db.query(User).filter(User.role == "member").all()
    assert len(org_admins) == 2
    assert len(members) == 2
    assert all(u.must_change_password for u in org_admins)
    assert all(u.org_id is not None for u in org_admins + members)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && python -m pytest tests/test_seed.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.seed_auth'`

- [ ] **Step 3: Implement**

Add to the `# Auth` section of `api/app/core/config.py` (inside the `Settings` class):

```python
    SUPERADMIN_EMAIL: str = "admin@ai4sids.org"
    SUPERADMIN_PASSWORD: str = "change-me-now"
    SEED_DEMO_ORGS: bool = False
```

`api/app/seed_auth.py`:

```python
"""Seed the platform super-admin and (optionally) demo organizations.

Run standalone:  python -m app.seed_auth
Also called from the app lifespan on startup.
"""
from sqlalchemy.orm import Session

from app.core.auth import get_user_by_email, hash_password
from app.core.config import settings
from app.models import Organization, User

DEMO_ORGS = [
    ("Ministry of Environment", "admin@moe.gov.demo", "member@moe.gov.demo"),
    ("National Met Office", "admin@met.gov.demo", "member@met.gov.demo"),
]
DEMO_PASSWORD = "demo2024"


def seed_super_admin(db: Session) -> None:
    """Create the platform super-admin from env config, if absent."""
    if get_user_by_email(db, settings.SUPERADMIN_EMAIL):
        return
    db.add(
        User(
            email=settings.SUPERADMIN_EMAIL,
            hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
            role="super_admin",
            full_name="Platform Admin",
        )
    )
    db.commit()
    print(f"✅ Super-admin created: {settings.SUPERADMIN_EMAIL}")


def seed_demo_orgs(db: Session) -> None:
    """Create two demo orgs with an org_admin and a member each, if no
    organizations exist yet. Org admins must change password on first login."""
    if db.query(Organization).count() > 0:
        return
    for org_name, admin_email, member_email in DEMO_ORGS:
        org = Organization(name=org_name)
        db.add(org)
        db.flush()
        db.add(
            User(
                email=admin_email,
                hashed_password=hash_password(DEMO_PASSWORD),
                role="org_admin",
                org_id=org.id,
                must_change_password=True,
            )
        )
        db.add(
            User(
                email=member_email,
                hashed_password=hash_password(DEMO_PASSWORD),
                role="member",
                org_id=org.id,
            )
        )
    db.commit()
    print("✅ Demo organizations seeded")


if __name__ == "__main__":
    from app.core.db import SessionLocal, init_db

    init_db()
    session = SessionLocal()
    try:
        seed_super_admin(session)
        if settings.SEED_DEMO_ORGS:
            seed_demo_orgs(session)
    finally:
        session.close()
```

In `api/app/__init__.py`, inside the lifespan `try:` block, directly after the `seed_default_user(db)` call (same `db` session, before `finally`):

```python
            from app.seed_auth import seed_demo_orgs, seed_super_admin
            from app.core.config import settings as app_settings

            seed_super_admin(db)
            if app_settings.SEED_DEMO_ORGS:
                seed_demo_orgs(db)
```

- [ ] **Step 4: Run all backend tests, then the module itself**

Run: `cd api && python -m pytest tests -v`
Expected: all PASS

Run: `cd api && SEED_DEMO_ORGS=true DATABASE_URL=sqlite:///./seed_check.db python -m app.seed_auth && rm seed_check.db`
Expected: prints `✅ Super-admin created: admin@ai4sids.org` and `✅ Demo organizations seeded`

- [ ] **Step 5: Commit**

```bash
git add api/app/seed_auth.py api/app/core/config.py api/app/__init__.py api/tests/test_seed.py
git commit -m "feat(api): idempotent super-admin and demo-org seeding"
```

---

### Task 6: Frontend auth types and AuthContext with /auth/me

**Files:**
- Create: `frontend/src/lib/auth/types.ts`
- Modify: `frontend/src/lib/auth/AuthContext.tsx`
- Test: `frontend/src/lib/auth/__tests__/AuthContext.test.tsx`

**Interfaces:**
- Consumes: `GET /auth/me` and `POST /auth/token` shapes from Task 4.
- Produces: `Role`, `AuthUser` types; `useAuth()` returns `{ token, user: AuthUser | null, isAuthenticated, isLoading, hasRole(...roles: Role[]): boolean, login(email, password): Promise<void>, logout(): void, refreshUser(): Promise<void> }`. Tasks 7–9 consume `useAuth`.

- [ ] **Step 1: Write failing tests**

`frontend/src/lib/auth/__tests__/AuthContext.test.tsx`:

```tsx
import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider, useAuth } from '../AuthContext'
import type { ReactNode } from 'react'

const wrapper = ({ children }: { children: ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

const ME = {
  id: 1,
  email: 'oa@met.org',
  full_name: 'Org Admin',
  role: 'org_admin',
  org: { id: 2, name: 'Met Office' },
  must_change_password: false,
}

function mockFetch(routes: Record<string, { status: number; body: unknown }>) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    const match = Object.entries(routes).find(([path]) => url.includes(path))
    if (!match) throw new Error(`Unexpected fetch: ${url}`)
    const { status, body } = match[1]
    return new Response(JSON.stringify(body), { status })
  })
}

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('AuthContext', () => {
  it('login stores token and loads the user from /auth/me', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/token': { status: 200, body: { access_token: 'tok-1', token_type: 'bearer' } },
        '/auth/me': { status: 200, body: ME },
      }),
    )
    const { result } = renderHook(() => useAuth(), { wrapper })
    await act(() => result.current.login('oa@met.org', 'pw'))
    await waitFor(() => expect(result.current.user).not.toBeNull())
    expect(localStorage.getItem('ai4sids_token')).toBe('tok-1')
    expect(result.current.user?.role).toBe('org_admin')
    expect(result.current.hasRole('org_admin')).toBe(true)
    expect(result.current.hasRole('super_admin')).toBe(false)
  })

  it('super_admin passes every hasRole check', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/token': { status: 200, body: { access_token: 't', token_type: 'bearer' } },
        '/auth/me': { status: 200, body: { ...ME, role: 'super_admin', org: null } },
      }),
    )
    const { result } = renderHook(() => useAuth(), { wrapper })
    await act(() => result.current.login('root@x.org', 'pw'))
    await waitFor(() => expect(result.current.user).not.toBeNull())
    expect(result.current.hasRole('member')).toBe(true)
    expect(result.current.hasRole('org_admin')).toBe(true)
  })

  it('a 401 from /auth/me clears the session', async () => {
    localStorage.setItem('ai4sids_token', 'stale-token')
    vi.stubGlobal(
      'fetch',
      mockFetch({ '/auth/me': { status: 401, body: { detail: 'nope' } } }),
    )
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.isAuthenticated).toBe(false)
    expect(localStorage.getItem('ai4sids_token')).toBeNull()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd frontend && pnpm test`
Expected: FAIL — `useAuth()` has no `user` / `hasRole` / `isLoading`.

- [ ] **Step 3: Implement**

`frontend/src/lib/auth/types.ts`:

```ts
export type Role = 'super_admin' | 'org_admin' | 'member'

export interface AuthUser {
  id: number
  email: string
  full_name: string | null
  role: Role
  org: { id: number; name: string } | null
  must_change_password: boolean
}
```

`frontend/src/lib/auth/AuthContext.tsx` — replace the whole file:

```tsx
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import type { AuthUser, Role } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TOKEN_KEY = 'ai4sids_token'

interface AuthContextValue {
  token: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  hasRole: (...roles: Role[]) => boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(() => !!localStorage.getItem(TOKEN_KEY))

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
    setIsLoading(false)
  }, [])

  const fetchMe = useCallback(
    async (activeToken: string) => {
      setIsLoading(true)
      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${activeToken}` },
        })
        if (res.status === 401) {
          logout()
          return
        }
        if (!res.ok) throw new Error(`Failed to load user: ${res.status}`)
        setUser((await res.json()) as AuthUser)
      } finally {
        setIsLoading(false)
      }
    },
    [logout],
  )

  useEffect(() => {
    if (token) void fetchMe(token)
  }, [token, fetchMe])

  const login = useCallback(async (email: string, password: string) => {
    const body = new URLSearchParams({ username: email, password })
    const res = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail ?? 'Invalid email or password')
    }

    const { access_token } = await res.json()
    localStorage.setItem(TOKEN_KEY, access_token)
    setToken(access_token)
  }, [])

  const refreshUser = useCallback(async () => {
    if (token) await fetchMe(token)
  }, [token, fetchMe])

  const hasRole = useCallback(
    (...roles: Role[]) => {
      if (!user) return false
      return user.role === 'super_admin' || roles.includes(user.role)
    },
    [user],
  )

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated: !!token,
        isLoading,
        hasRole,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd frontend && pnpm test`
Expected: all PASS (new AuthContext tests + existing suite)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/auth
git commit -m "feat(frontend): AuthContext loads user from /auth/me with role helper"
```

---

### Task 7: Login page and dashboard route guard

**Files:**
- Create: `frontend/src/routes/login.tsx`
- Create: `frontend/src/features/auth/LoginPage.tsx`
- Modify: `frontend/src/routes/dashboard/route.tsx`

**Interfaces:**
- Consumes: `useAuth().login` from Task 6.
- Produces: `/login` route with `?redirect=` search param; `/dashboard/*` redirects unauthenticated visitors to `/login`. Task 8 builds on the same guard pattern.

- [ ] **Step 1: Implement the login page**

`frontend/src/features/auth/LoginPage.tsx`:

```tsx
import { useState, type FormEvent } from 'react'
import { useNavigate, useSearch } from '@tanstack/react-router'
import { Waves } from 'lucide-react'
import { useAuth } from '@/lib/auth/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const { redirect: redirectTo } = useSearch({ from: '/login' })
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(email, password)
      await navigate({ to: redirectTo })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-xl dark:bg-slate-800">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
            <Waves className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-white">AI4SIDS-Gov</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Climate Resilience &amp; Preparedness Platform
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
            />
          </div>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

`frontend/src/routes/login.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { LoginPage } from '@/features/auth/LoginPage'

export const Route = createFileRoute('/login')({
  validateSearch: (search: Record<string, unknown>) => ({
    redirect: typeof search.redirect === 'string' ? search.redirect : '/dashboard',
  }),
  component: LoginPage,
})
```

- [ ] **Step 2: Enable the dashboard guard**

`frontend/src/routes/dashboard/route.tsx` — replace the whole file:

```tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { GovLayout } from '@/features/shell/components/GovLayout'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ location }) => {
    if (!localStorage.getItem('ai4sids_token')) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
  },
  component: GovLayout,
})
```

- [ ] **Step 3: Verify manually and with the suite**

Run: `cd frontend && pnpm test`
Expected: all PASS (route tree regenerates on dev/test run via the router plugin)

Run: `cd frontend && pnpm dev` — open `http://localhost:3000/dashboard` (or the printed port) in a private window.
Expected: redirected to `/login?redirect=%2Fdashboard`; logging in with the seeded demo user (`researcher@ai4sids.org` / `demo2024`, requires the API running) lands back on `/dashboard`.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/routes/login.tsx frontend/src/features/auth frontend/src/routes/dashboard/route.tsx frontend/src/routeTree.gen.ts
git commit -m "feat(frontend): login page and dashboard auth guard"
```

---

### Task 8: Forced change-password gate

**Files:**
- Create: `frontend/src/routes/change-password.tsx`
- Create: `frontend/src/features/auth/ChangePasswordPage.tsx`
- Create: `frontend/src/features/auth/RequirePasswordFresh.tsx`
- Modify: `frontend/src/routes/dashboard/route.tsx` (wrap layout with the gate)
- Test: `frontend/src/features/auth/__tests__/ChangePasswordPage.test.tsx`

**Interfaces:**
- Consumes: `useAuth()` (`user`, `token`, `refreshUser`, `isLoading`) from Task 6; `POST /auth/change-password` from Task 4.
- Produces: `/change-password` route; `RequirePasswordFresh` wrapper that redirects flagged users there from any dashboard page.

- [ ] **Step 1: Write failing test**

`frontend/src/features/auth/__tests__/ChangePasswordPage.test.tsx`:

```tsx
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ChangePasswordForm } from '../ChangePasswordPage'

describe('ChangePasswordForm', () => {
  it('submits current and new password with the bearer token', async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify({ status: 'password_changed' }), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const onSuccess = vi.fn()

    render(<ChangePasswordForm token="tok-9" onSuccess={onSuccess} />)
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'temp1234' },
    })
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'brand-new-pw-9' },
    })
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'brand-new-pw-9' },
    })
    fireEvent.click(screen.getByRole('button', { name: /update password/i }))

    await waitFor(() => expect(onSuccess).toHaveBeenCalled())
    const [url, init] = fetchMock.mock.calls[0]
    expect(String(url)).toContain('/auth/change-password')
    expect((init as RequestInit).headers).toMatchObject({
      Authorization: 'Bearer tok-9',
    })
    expect(JSON.parse((init as RequestInit).body as string)).toEqual({
      current_password: 'temp1234',
      new_password: 'brand-new-pw-9',
    })
  })

  it('blocks mismatched confirmation without calling the API', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    render(<ChangePasswordForm token="tok-9" onSuccess={vi.fn()} />)
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'temp1234' },
    })
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'one-password-1' },
    })
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'different-2' },
    })
    fireEvent.click(screen.getByRole('button', { name: /update password/i }))

    expect(await screen.findByText(/do not match/i)).toBeDefined()
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test`
Expected: FAIL — `ChangePasswordForm` does not exist.

- [ ] **Step 3: Implement**

`frontend/src/features/auth/ChangePasswordPage.tsx`:

```tsx
import { useState, type FormEvent } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useAuth } from '@/lib/auth/AuthContext'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function ChangePasswordForm({
  token,
  onSuccess,
}: {
  token: string
  onSuccess: () => void
}) {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (next !== confirm) {
      setError('New passwords do not match')
      return
    }
    setSubmitting(true)
    try {
      const res = await fetch(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ current_password: current, new_password: next }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail ?? 'Could not change password')
      }
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not change password')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="current" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Current password
        </label>
        <input
          id="current"
          type="password"
          required
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
        />
      </div>
      <div>
        <label htmlFor="next" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          New password
        </label>
        <input
          id="next"
          type="password"
          required
          minLength={8}
          value={next}
          onChange={(e) => setNext(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
        />
      </div>
      <div>
        <label htmlFor="confirm" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Confirm new password
        </label>
        <input
          id="confirm"
          type="password"
          required
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
        />
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {submitting ? 'Updating…' : 'Update password'}
      </button>
    </form>
  )
}

export function ChangePasswordPage() {
  const { token, refreshUser } = useAuth()
  const navigate = useNavigate()

  if (!token) return null

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-xl dark:bg-slate-800">
        <h1 className="mb-1 text-lg font-bold text-slate-900 dark:text-white">
          Set a new password
        </h1>
        <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
          You must change your temporary password before continuing.
        </p>
        <ChangePasswordForm
          token={token}
          onSuccess={() => {
            void refreshUser().then(() => navigate({ to: '/dashboard' }))
          }}
        />
      </div>
    </div>
  )
}
```

`frontend/src/routes/change-password.tsx`:

```tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { ChangePasswordPage } from '@/features/auth/ChangePasswordPage'

export const Route = createFileRoute('/change-password')({
  beforeLoad: () => {
    if (!localStorage.getItem('ai4sids_token')) {
      throw redirect({ to: '/login', search: { redirect: '/dashboard' } })
    }
  },
  component: ChangePasswordPage,
})
```

`frontend/src/features/auth/RequirePasswordFresh.tsx`:

```tsx
import { useEffect, type ReactNode } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useAuth } from '@/lib/auth/AuthContext'

/** Redirects users flagged must_change_password to the change-password
 * screen. Renders nothing while the user profile is still loading so
 * flagged users never see a flash of dashboard content. */
export function RequirePasswordFresh({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && user?.must_change_password) {
      void navigate({ to: '/change-password' })
    }
  }, [isLoading, user, navigate])

  if (isLoading || user?.must_change_password) return null
  return children
}
```

`frontend/src/routes/dashboard/route.tsx` — replace the whole file:

```tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { GovLayout } from '@/features/shell/components/GovLayout'
import { RequirePasswordFresh } from '@/features/auth/RequirePasswordFresh'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ location }) => {
    if (!localStorage.getItem('ai4sids_token')) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
  },
  component: DashboardShell,
})

function DashboardShell() {
  return (
    <RequirePasswordFresh>
      <GovLayout />
    </RequirePasswordFresh>
  )
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd frontend && pnpm test`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/routes/change-password.tsx frontend/src/features/auth frontend/src/routes/dashboard/route.tsx frontend/src/routeTree.gen.ts
git commit -m "feat(frontend): forced change-password gate for temp credentials"
```

---

### Task 9: Role-gated navigation

**Files:**
- Modify: `frontend/src/features/shell/types.ts` (NavItem gains `roles?: Role[]`)
- Modify: `frontend/src/features/shell/nav.ts` (add `filterNavByRole`)
- Modify: `frontend/src/features/shell/components/GovSidebar.tsx` (filter by current role)
- Test: `frontend/src/features/shell/__tests__/nav-roles.test.ts` (new file — do not touch the existing `nav.test.ts`)

**Interfaces:**
- Consumes: `Role` from `@/lib/auth/types`, `useAuth` from Task 6.
- Produces: `filterNavByRole(items: NavItem[], role: Role | null): NavItem[]`. No NAV_ITEMS entry gets a `roles` value in this project — the org-management item (project 2) will be the first consumer.

- [ ] **Step 1: Write failing tests**

`frontend/src/features/shell/__tests__/nav-roles.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import { LayoutDashboard } from 'lucide-react'
import { filterNavByRole } from '../nav'
import type { NavItem } from '../types'

describe('filterNavByRole', () => {
  const items: NavItem[] = [
    { label: 'Open', to: '/a', icon: LayoutDashboard },
    { label: 'Admins', to: '/b', icon: LayoutDashboard, roles: ['org_admin'] },
    { label: 'Platform', to: '/c', icon: LayoutDashboard, roles: ['super_admin'] },
  ]

  it('unrestricted items are visible to everyone, even logged-out', () => {
    expect(filterNavByRole(items, null).map((i) => i.label)).toEqual(['Open'])
  })

  it('member sees only unrestricted items', () => {
    expect(filterNavByRole(items, 'member').map((i) => i.label)).toEqual(['Open'])
  })

  it('org_admin sees org_admin items but not super_admin items', () => {
    expect(filterNavByRole(items, 'org_admin').map((i) => i.label)).toEqual([
      'Open',
      'Admins',
    ])
  })

  it('super_admin sees everything', () => {
    expect(filterNavByRole(items, 'super_admin').map((i) => i.label)).toEqual([
      'Open',
      'Admins',
      'Platform',
    ])
  })
})
```

Semantics: items without `roles` are visible to everyone (including `role = null`, since the sidebar only renders inside the guarded dashboard); items with `roles` require a matching role or `super_admin`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd frontend && pnpm test`
Expected: FAIL — `filterNavByRole` is not exported; `NavItem` has no `roles` field (type error).

- [ ] **Step 3: Implement**

In `frontend/src/features/shell/types.ts`, add the import at the top and extend `NavItem`:

```ts
import type { Role } from '@/lib/auth/types'
```

```ts
export interface NavItem {
  label: string
  to: string
  icon: LucideIcon
  badge?: number
  /** If set, only these roles (plus super_admin) see the item. */
  roles?: Role[]
}
```

In `frontend/src/features/shell/nav.ts`, add the import and the function (NAV_ITEMS unchanged):

```ts
import type { Role } from '@/lib/auth/types'

export function filterNavByRole(items: NavItem[], role: Role | null): NavItem[] {
  return items.filter((item) => {
    if (!item.roles) return true
    if (!role) return false
    return role === 'super_admin' || item.roles.includes(role)
  })
}
```

In `frontend/src/features/shell/components/GovSidebar.tsx`, add the imports and switch the nav render to the filtered list:

```tsx
import { NAV_ITEMS, filterNavByRole } from '@/features/shell/nav'
import { useAuth } from '@/lib/auth/AuthContext'
```

Inside `GovSidebar`, before the `return`:

```tsx
  const { user } = useAuth()
  const items = filterNavByRole(NAV_ITEMS, user?.role ?? null)
```

And change the map source from `NAV_ITEMS.map(...)` to `items.map(...)`.

- [ ] **Step 4: Run the full frontend suite**

Run: `cd frontend && pnpm test`
Expected: all PASS

- [ ] **Step 5: Full-stack sanity check**

Run the API: `cd api && SEED_DEMO_ORGS=true uvicorn app:app --port 8080`
Run the frontend: `cd frontend && VITE_API_URL=http://localhost:8080 pnpm dev`

Verify in a private browser window:
1. `/dashboard` redirects to `/login`.
2. Login as `admin@moe.gov.demo` / `demo2024` → forced to `/change-password`; after changing, lands on `/dashboard`.
3. Login as `member@moe.gov.demo` / `demo2024` → straight to `/dashboard`.
4. Login as `admin@ai4sids.org` / `change-me-now` → straight to `/dashboard` (super-admin).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/shell
git commit -m "feat(frontend): role-gated navigation filtering"
```
