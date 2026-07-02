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
