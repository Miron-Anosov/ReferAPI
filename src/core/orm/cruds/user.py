"""Users CRUD methods."""

import uuid
from typing import Optional

from sqlalchemy import Sequence, insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.orm.models.refer import ReferORM
from src.core.orm.models.user import UserORM


class Users:
    """CRUD operations for user management."""

    @staticmethod
    async def get_user(
        id_user: str, session: AsyncSession, user_table=UserORM
    ) -> Optional["UserORM"]:
        """Fetch a user by ID.

        Args:
            id_user (uuid.UUID): User ID to retrieve.
            session (AsyncSession): Active database session.
            user_table (UserORM): User ORM model (default is `UserORM`).

        Returns:
            Optional[UserORM]: User object if found, else `None`.
        """
        stmt = select(user_table).where(user_table.id == id_user)

        try:
            return await session.scalar(stmt)
        except (SQLAlchemyError, IntegrityError) as e:
            print(e)
            return None

    @staticmethod
    async def get_referred_by_user_id(
        id_user: str,
        session: AsyncSession,
        user_table: type[UserORM] = UserORM,
        ref_table: type[ReferORM] = ReferORM,
    ) -> Optional[Sequence["UserORM"]]:
        """Fetch users referred by a specific user ID.

        Args:
            id_user (uuid.UUID): ID of the referrer.
            session (AsyncSession): Active database session.
            user_table (UserORM): User ORM model (default is `UserORM`).
            ref_table (ReferORM): Referral ORM model (default is `ReferORM`).

        Returns:
            Optional[Sequence[UserORM]]: List of referred users or `None`.
        """
        stmt = (
            select(user_table)
            .where(user_table.id == ref_table.id_referrer)
            .where(user_table.id == id_user)
            .options(selectinload(user_table.referred_by))
        )

        try:
            result = await session.scalars(stmt)
            return result.all() if result else None
        except (SQLAlchemyError, IntegrityError) as e:
            print(e)
            return None

    @staticmethod
    async def new_user(
        id_user: str,
        user_name: str,
        session: AsyncSession,
        user_table: type[UserORM] = UserORM,
    ):
        """Add a new user to the database.

        Args:
            id_user (uuid.UUID): User ID.
            user_name (str): Name of the user.
            session (AsyncSession): Active database session.
            user_table (UserORM): User ORM model (default is `UserORM`).
        """
        await session.execute(
            insert(user_table),
            params=[{"id": id_user, "name": user_name}],
        )
