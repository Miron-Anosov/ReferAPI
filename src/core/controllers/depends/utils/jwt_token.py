"""TODO DOCS."""

import datetime

import jwt

from src.core.settings.constants import JWT
from src.core.settings.env import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt.jwt_private,
    algorithm: str = settings.jwt.algorithm,
    expire_minutes: int = settings.jwt.access_token_expire_minutes,
    expire_delta: datetime.timedelta | None = None,
) -> str:
    """Return encoded token."""
    now = datetime.datetime.now(datetime.UTC)

    if expire_delta:
        expire = now + expire_delta
    else:
        expire = now + datetime.timedelta(minutes=expire_minutes)

    to_encode = payload.copy()
    to_encode[JWT.PAYLOAD_EXPIRE_KEY] = expire
    to_encode[JWT.PAYLOAD_IAT_KEY] = now
    encode = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encode


def decode_jwt(
    jwt_token: str | bytes,
    public_key: str = settings.jwt.jwt_public,
    algorithm: str = settings.jwt.algorithm,
) -> dict:
    """Return decoded token."""
    decoded = jwt.decode(
        jwt=jwt_token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded


def create_auth_token(
    payload: dict,
    type_token: str,
    expire_minutes: int = settings.jwt.access_token_expire_minutes,
    expire_delta: datetime.timedelta | None = None,
) -> str:
    """Create new jwt token ot refresh token.

    Args:
        type_token (str): access or refresh.
        payload (dict): payload token.
        expire_minutes (int): for access token.
        expire_delta (int): for refresh token.
    Returns:
        jwt token (str)
    """
    jwt_payload = {JWT.TOKEN_TYPE_FIELD: type_token}
    jwt_payload.update(payload)
    set_expire_delta: datetime.timedelta | None = (
        expire_delta
        if type_token == JWT.TOKEN_TYPE_ACCESS
        else datetime.timedelta(days=settings.jwt.refresh_token_expire_days)
    )

    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_delta=set_expire_delta,
    )


def create_referral_token(
    payload: dict,
    type_token: str,
) -> str:
    """Create new referral token.

    Args:
        type_token (str): access or refresh.
        payload (dict): payload token.
    Returns:
        jwt token (str)
    """
    jwt_payload = {JWT.TOKEN_TYPE_FIELD: type_token}
    jwt_payload.update(payload)
    set_expire_delta = datetime.timedelta(
        days=settings.jwt.referral_token_expire_days
    )

    return encode_jwt(
        payload=jwt_payload,
        expire_delta=set_expire_delta,
    )
