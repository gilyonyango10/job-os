from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
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
    _ensure_sqlite_columns()


def _ensure_sqlite_columns() -> None:
    """Add columns create_all cannot attach to an existing SQLite file."""
    if not settings.database_url.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if "job_requirements" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("job_requirements")}
    if "evidence_text" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE job_requirements ADD COLUMN evidence_text TEXT"))
