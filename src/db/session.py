from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import get_settings
from src.db.models import Base


@lru_cache(maxsize=4)
def _engine_for_url(database_url: str):
    db_path = database_url.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


def get_engine():
    return _engine_for_url(get_settings().sqlite_database_url)


@lru_cache(maxsize=4)
def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def reset_db_caches() -> None:
    """Clear cached engines (tests / settings changes)."""
    _engine_for_url.cache_clear()
    get_session_factory.cache_clear()


def init_db() -> None:
    Base.metadata.create_all(bind=get_engine())
