"""Dependent for new users."""

import uuid
from typing import TYPE_CHECKING, Annotated, Optional

import pydantic
from fastapi import Depends, Form

from src.core.controllers.depends.utils.check_valid_ref import (
    user_return_from_token_in_chash_or_response_422,
)
from src.core.controllers.depends.utils.connect_db import get_crud, get_session
from src.core.controllers.depends.utils.hash_password import hash_pwd
from src.core.controllers.depends.utils.return_error import (
    raise_400_bad_req,
    valid_password_or_error_422,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.core.orm.crud import Crud


async def new_user(
    crud: Annotated["Crud", Depends(get_crud)],
    session: Annotated["AsyncSession", Depends(get_session)],
    name: Annotated[
        str,
        Form(
            description="Author's name: English, digits and one underscore.",
            min_length=2,
            max_length=15,
            pattern=r"^[a-zA-Z0-9_]+$",
        ),
    ],
    email: Annotated[
        pydantic.EmailStr,
        Form(
            description="User's email.",
        ),
    ],
    password: Annotated[
        str,
        Form(
            min_length=8,
            max_length=64,
            description="User's secret.",
        ),
    ],
    password_control: Annotated[
        str,
        Form(
            min_length=8,
            max_length=64,
            description="User's secret for check both.",
        ),
    ],
    referral: (
        Annotated[
            str | None,
            Form(
                min_length=8,
                max_length=1200,
                description="Referral code",
            ),
        ]
        | None
    ) = None,
) -> Optional[bool]:
    """Create a new user from form data.

    Args:
        name: User's name
        email: User's email address
        password: User's password
        password_control: Password confirmation
        referral: referral code
        crud: CRUD operations handler
        session: AsyncSession for database operations
    Returns:
        JSONResponse: Confirmation of user creation or error message
    Raises:
        HTTPException
    """
    valid_password_or_error_422(pwd=password, pwd2=password_control)

    password_hash: bytes = hash_pwd(password)
    new_user_ = dict(
        name=name,
        hashed_password=password_hash.decode(),
        email=email,
    )

    try:
        async with session.begin():
            new_uuid = uuid.uuid4().hex
            await crud.users.new_user(
                session=session,
                id_user=new_uuid,
                user_name=name,
            )

            await crud.auth.post_new_user(
                session=session,
                auth_user=new_user_,
                user_id=new_uuid,
            )

            if referral:
                referrer_id: str = (
                    await user_return_from_token_in_chash_or_response_422(
                        token=referral
                    )
                )

                await crud.refer.create_new_referral(
                    id_referrer=referrer_id,
                    id_referred=new_uuid,
                    session=session,
                )

        return True

    except Exception as e:
        print(f"Registration failed: {e}")
        raise_400_bad_req()
        return None
