from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import SessionDep
from app.models.organization import Organization
from app.models.user import User
from app.core.config import settings

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SECRET_KEY = getattr(settings, "SECRET_KEY", "changeme-set-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool

    model_config = {"from_attributes": True}

class OrgSummary(BaseModel):
    id: int
    name: str

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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# ---------------------------------------------------------------------------
# Current-user dependency (use in protected routes)
# ---------------------------------------------------------------------------

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

CurrentUser = Annotated[User, Depends(get_current_user)]

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Seed utility — call once on startup to ensure a default user exists
# ---------------------------------------------------------------------------

def seed_default_user(db: Session) -> None:
    """Create the default demo user if it doesn't already exist."""
    default_email = getattr(settings, "DEFAULT_USER_EMAIL", "researcher@ai4sids.org")
    default_password = getattr(settings, "DEFAULT_USER_PASSWORD", "demo2024")

    if not get_user_by_email(db, default_email):
        user = User(
            email=default_email,
            hashed_password=hash_password(default_password),
        )
        db.add(user)
        db.commit()
        print(f"✅ Default user created: {default_email}")
