"""SQLAlchemy UserORM model."""

from typing import TYPE_CHECKING

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.orm.models.base import BaseModel

if TYPE_CHECKING:
    from src.core.orm.models.refer import ReferORM


class UserORM(BaseModel):
    """User ORM model."""

    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    referred_by: Mapped[list["ReferORM"]] = relationship(
        "ReferORM",
        foreign_keys="[ReferORM.id_referred]",
        back_populates="referred_user",
        overlaps="referred_user",
    )

    invited_by: Mapped[list["ReferORM"]] = relationship(
        "ReferORM",
        foreign_keys="[ReferORM.id_referrer]",
        back_populates="referrer",
        overlaps="referrer",
    )
