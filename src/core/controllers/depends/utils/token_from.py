"""Get token from request."""

from fastapi import Request

from src.core.controllers.depends.utils.jwt_token import decode_jwt
from src.core.settings.constants import JWT, Keys


def get_user_id_from_token(request: Request):
    """Get user id from token."""
    token = request.headers.get(Keys.AUTH_HEADER)[
        Keys.AUTH_HEADER_PREF_BEARER :  # noqa E203
    ]
    data_token = decode_jwt(jwt_token=token)
    type_token = data_token.pop(JWT.TOKEN_TYPE_FIELD)
    if type_token == JWT.TOKEN_TYPE_ACCESS:
        return data_token.get(JWT.PAYLOAD_SUB_KEY)
