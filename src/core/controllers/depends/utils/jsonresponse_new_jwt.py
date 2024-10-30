"""Return Response with tokens."""

from fastapi import status
from fastapi.responses import JSONResponse

from src.core.controllers.depends.utils.jwt_token import (
    create_auth_token,
    create_referral_token,
)
from src.core.settings.constants import JWT, MimeTypes
from src.core.validators.token import TokenAuth, TokenReferral


def response_auth_tokens(payload: dict) -> "JSONResponse":
    """Return JSONResponse with new tokens."""
    user_token = TokenAuth(
        access_token=create_auth_token(
            payload=payload, type_token=JWT.TOKEN_TYPE_ACCESS
        ),
        refresh_token=create_auth_token(
            payload=payload, type_token=JWT.TOKEN_TYPE_REFRESH
        ),
    )

    resp = JSONResponse(
        content=user_token.model_dump(
            exclude={
                JWT.TOKEN_TYPE_REFRESH,
                JWT.DESCRIPTION_PYDANTIC_EXPIRE_REFRESH,
            }
        ),
        status_code=status.HTTP_201_CREATED,
        media_type=MimeTypes.APPLICATION_JSON,
    )
    resp.set_cookie(
        key=JWT.TOKEN_TYPE_REFRESH,
        value=user_token.refresh_token,
        httponly=True,
        expires=user_token.expires_refresh,
    )
    return resp


def response_referral_tokens(payload: dict) -> "TokenReferral":
    """Return JSONResponse with new referral token."""
    return TokenReferral(
        referral_token=create_referral_token(
            payload=payload,
            type_token=JWT.TOKEN_TYPE_REFERRAL,
        ),
    )
