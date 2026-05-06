from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from python.config import get_settings


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)


def get_db() -> Generator[Connection | None, None, None]:
    try:
        with engine.connect() as connection:
            yield connection
    except SQLAlchemyError:
        yield None

