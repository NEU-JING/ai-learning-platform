from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Base

# Use DATABASE_URL from settings (supports both SQLite and PostgreSQL)
_engine_url = settings.DATABASE_URL

# SQLite-specific connect args; other dialects don't need it
_connect_args = {}
if _engine_url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(_engine_url, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that yields a DB session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables — used only for dev bootstrap. Production uses Alembic."""
    Base.metadata.create_all(bind=engine)
