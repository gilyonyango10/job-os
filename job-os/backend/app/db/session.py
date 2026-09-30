from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db.base import Base

# SQLite needs this flag for FastAPI's multi-threaded request handling.
# PostgreSQL ignores connect_args that it does not understand, so keep
# the extra argument local to SQLite URLs only.
connect_args: dict[str, object] = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they do not exist.

    This is enough for the SQLite vertical slice. Alembic can be added
    when PostgreSQL and schema migrations become necessary.
    """
    from app import models as _models  # noqa: F401

    Base.metadata.create_all(bind=engine)
