from sqlalchemy import create_engine
from app.core.config import DB_URL


def _create_engine():
    if not DB_URL or DB_URL == "your_database_connection_string":
        raise RuntimeError(
            "DB_URL is not configured. Update .env with a valid SQLAlchemy connection string."
        )

    return create_engine(
        DB_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )


class LazyEngine:
    def __init__(self):
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            self._engine = _create_engine()
        return self._engine

    def connect(self):
        return self._get_engine().connect()

    def __getattr__(self, name):
        return getattr(self._get_engine(), name)


engine = LazyEngine()
