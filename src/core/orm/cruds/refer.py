"""Refer CRUD methods."""

import uuid

from sqlalchemy import Sequence, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.orm.models.refer import ReferORM


class Refer:
    """CRUD operations for referral management."""

    @staticmethod
    async def create_new_referral(
        id_referrer: str,
        id_referred: str,
        session: AsyncSession,
        refer_table: type[ReferORM] = ReferORM,
    ) -> bool:
        """Add a new referral record.

        Args:
            id_referrer (str): Referrer's user ID.
            id_referred (str): Referred user's ID.
            session (AsyncSession): Database session.
            refer_table (ReferORM): Referral ORM model (default is `ReferORM`).

        Returns:
            bool: `True` if creation is successful.
        """
        stmt = insert(refer_table).values(
            id=uuid.uuid4().hex,
            id_referrer=id_referrer,
            id_referred=id_referred,
        )

        await session.execute(stmt)
        return True

    @staticmethod
    async def get_referrals_by_user_id(
        session: AsyncSession,
        user_id: str,
        refer_table: type[ReferORM] = ReferORM,
    ) -> Sequence[ReferORM]:
        """Fetch referrals by user ID.

        Args:
            session (AsyncSession): Database session.
            user_id (str): Referrer's user ID.
            refer_table (ReferORM): Referral ORM model (default is `ReferORM`).

        Returns:
            Sequence[ReferORM]: List of referral records.
        """
        stmt = (
            select(refer_table)
            .where(refer_table.id_referrer == user_id)
            .options(
                selectinload(refer_table.referred_user),
                selectinload(refer_table.referrer),
            )
        )

        referrals = await session.execute(stmt)
        return referrals.scalars().all()
