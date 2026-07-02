"""Org management routes.

Org CRUD is super_admin only. Org-user routes allow super_admin or the
org_admin of that specific org (require_role passes super_admin implicitly;
require_org_access pins org_admins to their own org).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.auth import CurrentUser
from app.core.db import SessionDep
from app.core.permissions import (
    ROLE_ORG_ADMIN,
    require_org_access,
    require_role,
)
from app.features.orgs import service
from app.features.orgs.models import (
    OrgCreate,
    OrgOut,
    OrgUpdate,
    OrgUserCreate,
    OrgUserCreated,
    OrgUserOut,
    OrgUserUpdate,
    TempPasswordOut,
)
from app.models import User

router = APIRouter(prefix="/api/orgs", tags=["orgs"])

SuperAdmin = Annotated[User, Depends(require_role())]
OrgAdminUp = Annotated[User, Depends(require_role(ROLE_ORG_ADMIN))]


@router.get("", response_model=list[OrgOut])
async def list_orgs(current_user: SuperAdmin, db: SessionDep):
    return service.list_orgs(db)


@router.post("", response_model=OrgOut, status_code=status.HTTP_201_CREATED)
async def create_org(body: OrgCreate, current_user: SuperAdmin, db: SessionDep):
    return service.create_org(db, body.name, body.description)


@router.patch("/{org_id}", response_model=OrgOut)
async def update_org(
    org_id: int, body: OrgUpdate, current_user: SuperAdmin, db: SessionDep
):
    return service.update_org(db, org_id, body.model_dump(exclude_unset=True))


@router.get("/{org_id}/users", response_model=list[OrgUserOut])
async def list_org_users(org_id: int, current_user: OrgAdminUp, db: SessionDep):
    require_org_access(org_id, current_user)
    return service.list_org_users(db, org_id)


@router.post(
    "/{org_id}/users",
    response_model=OrgUserCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_org_user(
    org_id: int, body: OrgUserCreate, current_user: OrgAdminUp, db: SessionDep
):
    require_org_access(org_id, current_user)
    user, temp_password = service.create_org_user(
        db, org_id, body.email, body.full_name, body.role
    )
    return OrgUserCreated(
        **OrgUserOut.model_validate(user).model_dump(),
        temp_password=temp_password,
    )


@router.patch("/{org_id}/users/{user_id}", response_model=OrgUserOut)
async def update_org_user(
    org_id: int,
    user_id: int,
    body: OrgUserUpdate,
    current_user: OrgAdminUp,
    db: SessionDep,
):
    require_org_access(org_id, current_user)
    return service.update_org_user(
        db, org_id, user_id, current_user, body.model_dump(exclude_unset=True)
    )


@router.post("/{org_id}/users/{user_id}/reset-password", response_model=TempPasswordOut)
async def reset_org_user_password(
    org_id: int, user_id: int, current_user: OrgAdminUp, db: SessionDep
):
    require_org_access(org_id, current_user)
    temp_password = service.reset_org_user_password(db, org_id, user_id, current_user)
    return TempPasswordOut(temp_password=temp_password)
