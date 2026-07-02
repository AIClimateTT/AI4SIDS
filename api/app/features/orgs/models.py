"""Pydantic schemas for the org management API."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

AssignableRole = Literal["org_admin", "member"]


class OrgCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


class OrgUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class OrgOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    user_count: int

    model_config = {"from_attributes": True}


class OrgUserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    full_name: Optional[str] = None
    role: AssignableRole


class OrgUserUpdate(BaseModel):
    role: Optional[AssignableRole] = None
    is_active: Optional[bool] = None


class OrgUserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    must_change_password: bool
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class OrgUserCreated(OrgUserOut):
    temp_password: str


class TempPasswordOut(BaseModel):
    temp_password: str
