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
