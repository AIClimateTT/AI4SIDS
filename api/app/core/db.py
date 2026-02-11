from fastapi import Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Generator
from typing import Annotated

from app.core.config import settings
from app.models import Base

# Database configuration with connection pooling and timeouts
# For PostgreSQL: use proper pool settings to avoid connection hanging
engine_kwargs = {
    "pool_pre_ping": True,  # Verify connections before using them
    "pool_recycle": 300,    # Recycle connections after 5 minutes
    "connect_args": {
        "connect_timeout": 10,  # 10 second connection timeout
    }
}

# For SQLite: simpler configuration
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs = {
        "connect_args": {"check_same_thread": False}
    }

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

# Dependency to get a database session
def get_db() -> Generator[Session, None, None]:    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

SessionDep = Annotated[Session, Depends(get_db)]