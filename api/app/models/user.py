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
