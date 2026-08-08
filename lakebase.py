"""Lakebase connection helpers for the ticketing app."""

from __future__ import annotations

import base64
import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

try:
    from databricks.sdk import WorkspaceClient
except Exception:  # pragma: no cover - optional dependency in local runs
    WorkspaceClient = None

_w = WorkspaceClient() if WorkspaceClient is not None else None

_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")


def _lakebase_url() -> str:
    """Resolve the database URL from env vars or Databricks secrets."""
    env_url = os.environ.get("LAKEBASE_URL")
    if env_url:
        return env_url

    if _w is not None:
        try:
            secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
            return base64.b64decode(secret.value).decode("utf-8")
        except Exception:
            pass

    return os.environ.get("SQLITE_URL", "sqlite:///tickets.db")


def get_engine():
    """Return a SQLAlchemy engine for Lakebase or SQLite local development."""
    return create_engine(_lakebase_url(), pool_pre_ping=True)


def get_session_factory():
    """Create a session factory backed by the Lakebase engine."""
    engine = get_engine()
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_connection() -> Iterator[Session]:
    """Compatibility helper for local code paths."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
