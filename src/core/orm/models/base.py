"""SQLAlchemy BaseModel."""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase, AsyncAttrs):
    """BaseModel cheme ORM."""

    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        """View ORM object."""
        columns = [
            f"{row}={getattr(self, row)}"
            for row in self.__table__.columns.keys()
        ]
        return f"<{self.__class__.__name__}: {' '.join(columns)}>"
