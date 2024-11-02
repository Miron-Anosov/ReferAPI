"""Depends-Check active user."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.core.controllers.depends.utils.jsonresponse_new_jwt import (
    response_auth_tokens,
)
from src.core.controllers.depends.utils.jwt_token import decode_jwt
from src.core.controllers.depends.utils.return_error import raise_hht_401
from src.core.settings.constants import JWT, AuthRoutes, Prefix

oauth_bearer = OAuth2PasswordBearer(
    tokenUrl=f"{Prefix.API}{AuthRoutes.LOGIN_PATH}",
)

cookie_refresh = APIKeyCookie(name=JWT.TOKEN_TYPE_REFRESH)


async def token_is_alive(
    token: Annotated[str, Depends(oauth_bearer)],
) -> dict:
    """Validate token.

    Args:
        - token (str): HTTPBearer API key for authentication.
    Raises:
        HTTPException:
            - status 401
            - headers={"WWW-Authenticate": "Bearer"}
    """
    try:
        return decode_jwt(jwt_token=token)
    except InvalidTokenError:
        raise raise_hht_401()


async def refresh_token_is_alive(
    old_refresh_token: Annotated[str, Depends(cookie_refresh)],
) -> dict:
    """Validate token.

    Args:
        - token (str): HTTPBearer API key for authentication.
    Raises:
        HTTPException:
            - status 401
            - headers={"WWW-Authenticate": "Bearer"}
    """
    try:
        return decode_jwt(jwt_token=old_refresh_token)
    except InvalidTokenError:
        raise raise_hht_401()


async def up_tokens_by_refresh(
    token: Annotated[dict, Depends(refresh_token_is_alive)],
):
    """Token refresh update.

    Args:
        - token (str): Cookie API key for authentication.

    Raises:
        HTTPException:
            - status 401
            - headers="WWW-Authenticate": "Bearer realm=Refresh token expired"
    Notes:
        if token is not "refresh_token", it'll raise InvalidTokenError.
    """
    try:

        if token.get(JWT.TOKEN_TYPE_FIELD) == JWT.TOKEN_TYPE_REFRESH:
            token.pop(JWT.TOKEN_TYPE_FIELD)
            return response_auth_tokens(payload=token)
        raise InvalidTokenError

    except InvalidTokenError:
        raise raise_hht_401()
