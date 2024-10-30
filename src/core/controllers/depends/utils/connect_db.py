"""Get db session and CRUDs."""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from src.core.orm.crud import create_crud_helper
from src.core.orm.engine import get_engine
from src.core.settings.env import settings

if TYPE_CHECKING:
    from src.core.orm.crud import Crud
    from src.core.orm.engine import ManagerDB


def get_crud() -> "Crud":
    """Return CRUD worker."""
    return create_crud_helper()


async def _init_engine() -> "ManagerDB":
    return await get_engine(
        url=settings.db.get_url_database, echo=settings.db.ECHO
    )


async def disconnect_db() -> None:
    """Disconnect db."""
    connect = await get_engine(
        url=settings.db.get_url_database, echo=settings.db.ECHO
    )
    await connect.async_engine.dispose()


async def get_session(engine: Annotated["ManagerDB", Depends(_init_engine)]):
    """Return db session."""
    async with engine.get_scoped_session() as session:
        yield session
        await session.close()
