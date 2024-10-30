"""SQLAlchemy engine."""

import asyncio
from asyncio import current_task
from typing import Any, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.core.orm.models.auth import AuthORM  # noqa
from src.core.orm.models.base import BaseModel
from src.core.orm.models.user import UserORM  # noqa
from src.core.settings.env import settings


class ManagerDB:
    """Async engine manager."""

    _instance: Optional["ManagerDB"] = None

    def __new__(cls, *args, **kwargs):
        """Create singleton API."""
        if cls._instance is None:
            cls._instance = super(ManagerDB, cls).__new__(cls)
        return cls._instance

    def __init__(self, url: str, echo: bool) -> "None":
        """Init SQLAlchemy manager."""
        if not hasattr(self, "_initialize_tables"):
            self.__url = url
            self.__echo = echo
            self.async_engine = self.create_async_engine()
            self._session = self.create_session(self.async_engine)

            self._initialize_tables = False

    @staticmethod
    def create_session(
        engine: "AsyncEngine",
    ) -> "async_sessionmaker[AsyncSession]":
        """Create db session."""
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            class_=AsyncSession,
        )

    @property
    def get_scoped_session(self) -> async_scoped_session[AsyncSession | Any]:
        """Return current scope."""
        return async_scoped_session(
            session_factory=self.create_session(self.async_engine),
            scopefunc=current_task,
        )

    def create_async_engine(self) -> "AsyncEngine":
        """Create async engine."""
        return create_async_engine(
            url=self.__url,
            echo=self.__echo,
            pool_pre_ping=True,
            pool_size=settings.db.POOL_SIZE_SQL_ALCHEMY_CONF,
            pool_timeout=settings.db.POOL_TIMEOUT,
            max_overflow=settings.db.MAX_OVERFLOW,
        )

    async def initialize(self):
        """Initialize the database by creating tables."""
        if self._initialize_tables is False:
            await self._create_tables()
            self._initialize_tables = True

    async def _create_tables(self):
        """Create table if not exist."""
        async with self.async_engine.begin() as conn:
            # todo: add logger INIT DB TABLES
            await conn.run_sync(BaseModel.metadata.create_all)


lock = asyncio.Lock()


async def get_engine(url: str, echo: bool) -> "ManagerDB":
    """Create ORM session/engine manager."""
    async with lock:
        manager = ManagerDB(url=url, echo=echo)
        await manager.initialize()
    return manager
