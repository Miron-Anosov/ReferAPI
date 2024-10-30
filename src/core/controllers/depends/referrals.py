"""Depends for referrals by user ID."""

import json
from typing import TYPE_CHECKING, Annotated, cast

import pydantic
from fastapi import Depends, Header, Request, Response
from jwt.exceptions import InvalidTokenError

from src.core.controllers.depends.token import token_is_alive
from src.core.controllers.depends.utils.connect_db import get_crud, get_session
from src.core.controllers.depends.utils.jsonresponse_new_jwt import (
    response_referral_tokens,
)
from src.core.controllers.depends.utils.redis_chash import (
    cache_http_get,
    cache_http_singleton_value_by_user,
    is_alive_referral_token_in_chash,
)
from src.core.controllers.depends.utils.return_error import (
    raise_400_bad_req,
    raise_hht_401,
    raise_http_404,
    valid_id_or_error_422,
)
from src.core.orm.models.refer import ReferORM
from src.core.settings.constants import JWT, Keys, MessageError
from src.core.settings.env import settings
from src.core.validators.token import TokenReferral
from src.core.validators.user import User, UserReferrals

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.core.orm.crud import Crud


@cache_http_get(
    expire=JWT.EXP_BY_EMAIL_OR_ID,
    prefix_key=JWT.PREFIX_BY_EMAIL_OR_ID,
    request_query_params=True,
)
async def get_referrals_by_user_id(
    user_id: str,
    crud: Annotated["Crud", Depends(get_crud)],
    session: Annotated["AsyncSession", Depends(get_session)],
    request: Request,
    response: Response,
    if_none_match: str | None = Header(default=None),
) -> "UserReferrals":
    """Return referral users by user ID.

    Args:
        session: AsyncSession
        crud: Crud
        user_id: str
        request: Request
        response: Response
        if_none_match: Optional[str]
    Return:
        UserReferrals (access_token: str, token_type: str)
    """
    valid_id_or_error_422(id_data=user_id)
    user_data = await crud.refer.get_referrals_by_user_id(
        user_id=user_id, session=session
    )

    user_data = cast(list[ReferORM], user_data)

    if not user_data:
        print(request, response, if_none_match)
        raise_http_404(
            error_type=MessageError.TYPE_ERROR_404,
            error_message=MessageError.MESSAGE_NO_REFERRALS_FOUND,
        )

    referrals_by_user_id = [
        User(id=str(user.id_referred), name=user.referred_user.name)
        for user in user_data
    ]

    return UserReferrals(
        id=user_id,
        name=(
            user_data[Keys.REFERRER_INDEX].referrer.name if user_data else None
        ),
        referrals=referrals_by_user_id,
    )


@cache_http_get(
    expire=JWT.EXP_BY_EMAIL_OR_ID,
    prefix_key=JWT.PREFIX_BY_EMAIL_OR_ID,
    request_query_params=True,
)
async def referral_token_by_email(
    email: pydantic.EmailStr,
    crud: Annotated["Crud", Depends(get_crud)],
    session: Annotated["AsyncSession", Depends(get_session)],
    request: Request,
    response: Response,
    if_none_match: str | None = Header(default=None),
) -> "TokenReferral":
    """GET token by email.

    Args:
        email: User's email
        crud: Crud
        session: AsyncSession
        request: Request
        response: Response
        if_none_match: Optional[str]

    Raises:
        HTTPException:
            - status 401
            - headers="WWW-Authenticate": "Bearer realm=Refresh token expired"
    Notes:
        if token is not "refresh_token", it'll raise InvalidTokenError.
    """
    user_id_by_email = await crud.auth.get_user_id_by(
        email=email, session=session
    )
    if user_id_by_email is None:
        raise_http_404(
            error_type=MessageError.TYPE_ERROR_404,
            error_message=MessageError.INVALID_REF_TOKEN_ERR_MESSAGE,
        )
    try:
        token_data_from_chash = await is_alive_referral_token_in_chash(
            prefix_key=JWT.TOKEN_TYPE_REFERRAL,
            referral_owner_id=str(user_id_by_email),
        )
        if token_data_from_chash is None:
            raise_400_bad_req(
                error_type=MessageError.INVALID_TOKEN_ERR,
                error_message=MessageError.INVALID_REF_TOKEN_ERR_MESSAGE,
            )
        return TokenReferral(**json.loads(token_data_from_chash))

    except ValueError:
        print(request, response, if_none_match)
        raise_400_bad_req(
            error_type=MessageError.INVALID_TOKEN_ERR,
            error_message=MessageError.INVALID_REF_TOKEN_ERR_MESSAGE,
        )


@cache_http_singleton_value_by_user(
    expire=settings.jwt.set_referral_token_expire_days,
    prefix_key=JWT.TOKEN_TYPE_REFERRAL,
)
async def referral_token(
    token: Annotated[dict, Depends(token_is_alive)],
    request: Request,
    response: Response,
) -> "TokenReferral":
    """Referral token create.

    Args:
        - token (str): Access token for authentication.

    Raises:
        HTTPException:
            - status 401
            - headers="WWW-Authenticate": "Bearer realm=Refresh token expired"
    Notes:
        if token is not "refresh_token", it'll raise InvalidTokenError.
    """
    try:
        type_token = token.pop(JWT.TOKEN_TYPE_FIELD)
        if type_token == JWT.TOKEN_TYPE_ACCESS:
            payload = {
                JWT.PAYLOAD_SUB_KEY: token.pop(JWT.PAYLOAD_SUB_KEY),
            }
            return response_referral_tokens(payload=payload)

        raise InvalidTokenError

    except InvalidTokenError:
        print(request, response)
        raise raise_hht_401()
