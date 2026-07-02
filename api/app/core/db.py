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

# Dependency to get a database session
def get_db() -> Generator[Session, None, None]:    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

SessionDep = Annotated[Session, Depends(get_db)]