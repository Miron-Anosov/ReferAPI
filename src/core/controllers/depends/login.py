"""Depends for new users."""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.controllers.depends.utils.connect_db import get_crud, get_session
from src.core.controllers.depends.utils.hash_password import validate_pwd
from src.core.controllers.depends.utils.jsonresponse_new_jwt import (
    response_auth_tokens,
)
from src.core.controllers.depends.utils.return_error import http_exception
from src.core.settings.constants import JWT, MessageError

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.core.orm.crud import Crud


async def login_user_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    crud: Annotated["Crud", Depends(get_crud)],
    session: Annotated["AsyncSession", Depends(get_session)],
) -> "JSONResponse":
    """Check user in DB than create tokens.

    Args:
        form_data: OAuth2PasswordRequestForm
        session: AsyncSession
        crud: Crud
    Return:
        UserToken(access_token: str, token_type: str)
    Raises:
        HTTPException()
    Notes:
        Return new JWT access token and refresh token.
    """
    user_data = await crud.auth.login_user(
        email=form_data.username, session=session
    )

    if not isinstance(user_data, tuple):
        raise http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type=MessageError.TYPE_ERROR_INTERNAL_SERVER_ERROR,
            error_message=MessageError.MESSAGE_SERVER_ERROR,
        )

    user_hash_pwd, user_id = user_data

    if user_hash_pwd and validate_pwd(
        password=form_data.password,
        hash_password=user_hash_pwd.encode(),
    ):

        user_profile = await crud.users.get_user(
            id_user=user_id,
            session=session,
        )
        payload = {
            JWT.PAYLOAD_SUB_KEY: str(user_id),
            JWT.PAYLOAD_USERNAME_KEY: user_profile.name,
        }

        return response_auth_tokens(payload=payload)

    raise http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_type=MessageError.TYPE_ERROR_INVALID_AUTH,
        error_message=MessageError.INVALID_EMAIL_OR_PWD,
    )
