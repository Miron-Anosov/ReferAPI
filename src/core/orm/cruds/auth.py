"""Users CRUD methods."""

from sqlalchemy import bindparam, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.orm.models.auth import AuthORM


class AuthUsers:
    """CRUD operations for authentication users."""

    @staticmethod
    async def post_new_user(
        user_id: str,
        session: AsyncSession,
        auth_user: dict,
        table_auth: AuthORM = AuthORM,
    ) -> None:
        """Add a new user to the database.

        Args:
            user_id (str): Unique user ID.
            session (AsyncSession): Database session.
            auth_user (dict): User data for the auth table.
            table_auth (AuthORM): Auth ORM model (default is `AuthORM`).
        """
        auth_user["user_id"] = user_id
        await session.execute(insert(table_auth), params=[auth_user])

    @staticmethod
    async def login_user(
        email: str,
        session: AsyncSession,
        auth_user: type[AuthORM] = AuthORM,
    ) -> tuple:
        """Authenticate a user by email.

        Args:
            email (str): User email.
            session (AsyncSession): Database session.
            auth_user (AuthORM): Auth ORM model (default is `AuthORM`).

        Returns:
            tuple: User password hash and ID if exists, else `(None, None)`.
        """
        try:
            user: AuthORM = await session.scalar(
                statement=(
                    select(auth_user).where(
                        auth_user.email == bindparam("email")
                    )
                ),
                params={"email": email},
            )

            if user:
                return user.hashed_password, user.user_id

            return None, None

        except SQLAlchemyError as e:
            print(e)
            return None, None

    @staticmethod
    async def get_user_id_by(
        email: str,
        session: AsyncSession,
        auth_user: type[AuthORM] = AuthORM,
    ) -> str | None:
        """Retrieve user ID by email.

        Args:
            email (str): User email.
            session (AsyncSession): Database session.
            auth_user (AuthORM): Auth ORM model (default is `AuthORM`).

        Returns:
            str | None: User ID if found, else `None`.
        """
        try:
            statement = select(auth_user).where(
                auth_user.email == bindparam("email")
            )
            user: AuthORM = await session.scalar(
                statement, params={"email": email}
            )

            return str(user.user_id) if user else None

        except SQLAlchemyError as e:
            print(f"Error querying user by email: {e}")
            return None
