"""
Shared test fixtures. Nothing here is autouse: tests that do not ask for `db` are unaffected.

The `db` fixture is an in-memory SQLite database with the real models. PostgreSQL is the production
database, so a compile hook teaches SQLite to create the JSONB columns used by the older models.
"""
import itertools
from datetime import timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registers every model on Base.metadata)
from app.core.database import Base
from app.core.ratelimit import reset_rate_limits
from app.models.user import User


@compiles(JSONB, "sqlite")
def _compile_jsonb_for_sqlite(type_, compiler, **kw):
    return "JSON"


_user_numbers = itertools.count(1)


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # pysqlite's default transaction handling breaks SAVEPOINT (the first SAVEPOINT silently starts
    # and later commits the real transaction). These two hooks are SQLAlchemy's documented fix and
    # make nested transactions behave like they do on PostgreSQL.
    @event.listens_for(engine, "connect")
    def _no_implicit_begin(dbapi_connection, connection_record):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _explicit_begin(conn):
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(engine)
    # Same settings as app.core.database.SessionLocal (notably autoflush=False).
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def make_user(db, role="student", name="Asha Kumar"):
    """Create and commit a user with a unique e-mail address."""
    number = next(_user_numbers)
    user = User(
        email=f"learner{number}@example.com",
        hashed_password=None,
        full_name=name,
        role=role,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture(autouse=True)
def _fresh_rate_limits():
    """Rate-limit windows are per process and keyed by user id, which every test database reuses."""
    reset_rate_limits()
    yield
    reset_rate_limits()


@pytest.fixture
def no_farming_delays(monkeypatch):
    """
    Switch off the time-based anti-farming guards (quiz retry cooldown, lesson pace) so the many tests that
    read lessons or retake quizzes back to back see the plain XP rules. Tests for the guards themselves
    set the real values again.
    """
    from app.services import gamification

    monkeypatch.setattr(gamification, "QUIZ_RETRY_COOLDOWN", timedelta(0))
    monkeypatch.setattr(gamification, "LESSON_MIN_GAP", timedelta(0))
