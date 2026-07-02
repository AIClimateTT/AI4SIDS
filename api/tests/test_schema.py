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
