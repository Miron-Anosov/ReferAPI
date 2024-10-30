"""Check referral token."""

from jwt.exceptions import InvalidTokenError

from src.core.controllers.depends.utils.jwt_token import decode_jwt
from src.core.controllers.depends.utils.redis_chash import (
    is_alive_referral_token_in_chash,
)
from src.core.controllers.depends.utils.return_error import raise_http_404
from src.core.settings.constants import JWT, MessageError


async def user_return_from_token_in_chash_or_response_422(token: str) -> str:
    """Check for the existence of a referral token in the cache.

    Decodes the JWT token and verifies if it is a referral type.
    Then, checks if the token exists in the Redis cache. Raises an
    HTTP 404 error if validation fails.

    Args:
        token (str): The JWT token to decode and verify.

    Raises:
        HTTPException: A 404 error if the token is invalid or not
        found in the cache.
    """
    try:
        payload = decode_jwt(jwt_token=token)
        referral_token = payload.get(JWT.TOKEN_TYPE_FIELD)

        if referral_token != JWT.TOKEN_TYPE_REFERRAL:
            raise InvalidTokenError

        id_ref = payload.get(JWT.PAYLOAD_SUB_KEY)

        if (
            _ := await is_alive_referral_token_in_chash(
                referral_owner_id=id_ref, prefix_key=JWT.TOKEN_TYPE_REFERRAL
            )
            is False
        ):
            raise InvalidTokenError

        return id_ref

    except InvalidTokenError:
        raise raise_http_404(
            error_type=MessageError.INVALID_TOKEN_ERR,
            error_message=MessageError.INVALID_REF_TOKEN_ERR_MESSAGE,
        )
