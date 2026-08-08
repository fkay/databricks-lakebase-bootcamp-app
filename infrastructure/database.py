"""Database infrastructure helpers for the ticketing app."""

from __future__ import annotations

import base64
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

try:
    from databricks.sdk import WorkspaceClient
except Exception:  # pragma: no cover - optional dependency in local runs
    WorkspaceClient = None


class DatabaseConfig:
    def __init__(self) -> None:
        self.scope = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
        self.key = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")
        self.workspace_client = (WorkspaceClient()
                                 if (WorkspaceClient is not None
                                 and os.environ.get("LAKEBASE_URL") is None)
                                 else None)

    def get_database_url(self) -> str:
        env_url = os.environ.get("LAKEBASE_URL")
        if env_url:
            return env_url

        if self.workspace_client is not None:
            try:
                secret = self.workspace_client.secrets.get_secret(
                                            scope=self.scope, key=self.key)
                return base64.b64decode(secret.value).decode("utf-8")
            except Exception:
                pass

        return os.environ.get("SQLITE_URL", "sqlite:///tickets.db")


def get_session_factory() -> sessionmaker:
    config = DatabaseConfig()
    engine = create_engine(
                config.get_database_url(),
                connect_args={"options": "-csearch_path=tickets_app,public"},
                pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)
