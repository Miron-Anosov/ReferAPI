"""SQLAlchemy UserORM model."""

from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.orm.models.base import BaseModel

if TYPE_CHECKING:
    from src.core.orm.models.user import UserORM


class ReferORM(BaseModel):
    """Refer ORM model."""

    __tablename__ = "refer"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    id_referrer: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("users.id"), index=True, nullable=False
    )

    id_referred: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("users.id"), index=True, nullable=False
    )

    referred_user: Mapped["UserORM"] = relationship(
        "UserORM",
        foreign_keys=id_referred,
        back_populates="referred_by",
        overlaps="referred_by",
    )

    referrer: Mapped["UserORM"] = relationship(
        "UserORM",
        foreign_keys=id_referrer,
        back_populates="invited_by",
        overlaps="invited_by",
    )
