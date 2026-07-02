"""DB logic for org and org-user management.

Raises HTTPException directly; the controller stays a thin wiring layer.
Guard rails:
- only org_admin/member are assignable (schema-enforced, double-checked here)
- admins cannot modify their own account through these endpoints
- super_admin users are invisible to org-scoped lookups (they have no org)
"""
import secrets

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import hash_password
from app.models import Organization, User


def generate_temp_password() -> str:
    return secrets.token_urlsafe(9)


def _get_org_or_404(db: Session, org_id: int) -> Organization:
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
    return org


def _get_org_user_or_404(db: Session, org_id: int, user_id: int) -> User:
    user = (
        db.query(User).filter(User.id == user_id, User.org_id == org_id).first()
    )
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found in this organization")
    return user


def _forbid_self(actor: User, target_id: int) -> None:
    if actor.id == target_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Cannot modify your own account here"
        )


def list_orgs(db: Session) -> list[dict]:
    rows = (
        db.query(Organization, func.count(User.id))
        .outerjoin(User, User.org_id == Organization.id)
        .group_by(Organization.id)
        .order_by(Organization.name)
        .all()
    )
    return [
        {
            "id": org.id,
            "name": org.name,
            "description": org.description,
            "is_active": org.is_active,
            "created_at": org.created_at,
            "user_count": count,
        }
        for org, count in rows
    ]


def create_org(db: Session, name: str, description: str | None) -> dict:
    if db.query(Organization).filter(Organization.name == name).first():
        raise HTTPException(
            status.HTTP_409_CONFLICT, "An organization with this name already exists"
        )
    org = Organization(name=name, description=description)
    db.add(org)
    db.commit()
    db.refresh(org)
    return _org_dict(db, org)


def update_org(db: Session, org_id: int, changes: dict) -> dict:
    org = _get_org_or_404(db, org_id)
    new_name = changes.get("name")
    if new_name and new_name != org.name:
        if db.query(Organization).filter(Organization.name == new_name).first():
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "An organization with this name already exists",
            )
    for field in ("name", "description", "is_active"):
        if changes.get(field) is not None:
            setattr(org, field, changes[field])
    db.commit()
    db.refresh(org)
    return _org_dict(db, org)


def _org_dict(db: Session, org: Organization) -> dict:
    count = db.query(func.count(User.id)).filter(User.org_id == org.id).scalar()
    return {
        "id": org.id,
        "name": org.name,
        "description": org.description,
        "is_active": org.is_active,
        "created_at": org.created_at,
        "user_count": count,
    }


def list_org_users(db: Session, org_id: int) -> list[User]:
    _get_org_or_404(db, org_id)
    return (
        db.query(User).filter(User.org_id == org_id).order_by(User.email).all()
    )


def create_org_user(
    db: Session, org_id: int, email: str, full_name: str | None, role: str
) -> tuple[User, str]:
    org = _get_org_or_404(db, org_id)
    if not org.is_active:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Cannot add users to a deactivated organization",
        )
    if role not in ("org_admin", "member"):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Role not assignable"
        )
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A user with this email already exists"
        )
    temp_password = generate_temp_password()
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(temp_password),
        role=role,
        org_id=org_id,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, temp_password


def update_org_user(
    db: Session, org_id: int, user_id: int, actor: User, changes: dict
) -> User:
    _get_org_or_404(db, org_id)
    _forbid_self(actor, user_id)
    user = _get_org_user_or_404(db, org_id, user_id)
    role = changes.get("role")
    if role is not None:
        if role not in ("org_admin", "member"):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Role not assignable"
            )
        user.role = role
    if changes.get("is_active") is not None:
        user.is_active = changes["is_active"]
    db.commit()
    db.refresh(user)
    return user


def reset_org_user_password(
    db: Session, org_id: int, user_id: int, actor: User
) -> str:
    _get_org_or_404(db, org_id)
    _forbid_self(actor, user_id)
    user = _get_org_user_or_404(db, org_id, user_id)
    temp_password = generate_temp_password()
    user.hashed_password = hash_password(temp_password)
    user.must_change_password = True
    db.commit()
    return temp_password
