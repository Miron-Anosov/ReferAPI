"""Referral routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.core.controllers.depends.referrals import get_referrals_by_user_id
from src.core.controllers.depends.token import (
    referral_token,
    referral_token_by_email,
)
from src.core.settings.constants import (
    HTTPResponseGETReferrals,
    MimeTypes,
    ResponsesAuthUser,
    ResponsesGetRef,
    UserRefRoutes,
)
from src.core.validators.status_ok import Status
from src.core.validators.token import TokenAuth, TokenReferral
from src.core.validators.user import UserReferrals


def create_ref_route() -> APIRouter:
    """Create and return an APIRouter for user routes."""
    return APIRouter(tags=[UserRefRoutes.TAG])


ref: APIRouter = create_ref_route()


@ref.post(
    path=UserRefRoutes.REFERRAL_POST_PATH,
    status_code=status.HTTP_201_CREATED,
    response_model=TokenReferral,
    responses=ResponsesAuthUser.responses,
)
async def gen_referral(
    ref_token: Annotated[TokenReferral, Depends(referral_token)]
) -> JSONResponse:
    """Generate a new referral token.

    Args:
        ref_token (TokenAuth): Referral token dependency.

    Returns:
        JSONResponse: Response containing referral token.
    """
    return JSONResponse(
        content=ref_token.model_dump(),
        status_code=status.HTTP_201_CREATED,
        media_type=MimeTypes.APPLICATION_JSON,
    )


@ref.delete(
    path=UserRefRoutes.REFERRAL_DELETE_PATH,
    status_code=status.HTTP_200_OK,
    response_model=Status,
    responses=ResponsesAuthUser.responses,
)
async def del_referral(
    successful: Annotated[TokenAuth, Depends(referral_token)]
) -> JSONResponse:
    """Delete an existing referral token.

    Args:
        successful (TokenAuth): Referral token dependency.

    Returns:
        JSONResponse: Response indicating successful deletion.
    """
    return JSONResponse(
        content=Status(result=successful).model_dump(),
        status_code=status.HTTP_200_OK,
        media_type=MimeTypes.APPLICATION_JSON,
    )


@ref.get(
    path=UserRefRoutes.REFERRAL_TOKEN_GET_PATH_BY_EMAIL,
    status_code=status.HTTP_200_OK,
    response_model=TokenReferral,
    responses=HTTPResponseGETReferrals.responses,
)
async def get_referral_by_email(
    token: Annotated[TokenReferral, Depends(referral_token_by_email)]
) -> JSONResponse:
    """Get referral token by email.

    Args:
        token (TokenReferral): Token retrieved by email.

    Returns:
        JSONResponse: Response containing the referral token.
    """
    return JSONResponse(
        content=token.model_dump(),
        status_code=status.HTTP_201_CREATED,
        media_type=MimeTypes.APPLICATION_JSON,
    )


@ref.get(
    path=UserRefRoutes.REFERRAL_GET_PATH_BY_ID,
    status_code=status.HTTP_200_OK,
    response_model=TokenReferral,
    responses=ResponsesGetRef.responses,
)
async def get_referral_by_user_id(
    referrals: Annotated[UserReferrals, Depends(get_referrals_by_user_id)]
) -> JSONResponse:
    """Get referral token by user id.

    Args:
        referrals (UserReferrals): referrals clients.

    Returns:
        JSONResponse: Response containing the referral token.
    """
    return JSONResponse(
        content=referrals.model_dump(),
        status_code=status.HTTP_200_OK,
        media_type=MimeTypes.APPLICATION_JSON,
    )
