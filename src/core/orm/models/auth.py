"""SQLAlchemy UsersAuthORM model."""

from datetime import datetime

from sqlalchemy import UUID, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.orm.models.base import BaseModel


class AuthORM(BaseModel):
    """UsersAuthORM model."""

    __tablename__ = "auth"
    user_id: Mapped[str] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        primary_key=True,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    active: Mapped[bool] = mapped_column(default=True)
