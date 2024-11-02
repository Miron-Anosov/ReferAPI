"""Registration routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyCookie, HTTPBearer

from src.core.controllers.depends.login import login_user_form
from src.core.controllers.depends.token import up_tokens_by_refresh
from src.core.settings.constants import (
    JWT,
    AuthRoutes,
    Headers,
    Response500,
    ResponsesAuthUser,
)
from src.core.validators.status_ok import Status
from src.core.validators.token import TokenAuth


def create_auth_route() -> APIRouter:
    """Create auth route.

    Return:
    - APIRouter
    """
    return APIRouter(
        tags=[AuthRoutes.TAG],
    )


auth: APIRouter = create_auth_route()


@auth.post(
    path=AuthRoutes.LOGIN_PATH,
    status_code=status.HTTP_200_OK,
    response_model=TokenAuth,
    responses=ResponsesAuthUser.responses,
)
async def login_form(
    users_tokens: Annotated["JSONResponse", Depends(login_user_form)],
) -> "JSONResponse":
    """**Post loging user**.

    **Body**:
    - `name` (str): user's name.
    - `password` (str): user's secret.

    Set Cookie:  `refresh_token`
    """
    return users_tokens


@auth.patch(
    path=AuthRoutes.TOKEN_PATH,
    status_code=status.HTTP_201_CREATED,
    response_model=TokenAuth,
    responses=ResponsesAuthUser.responses,
)
async def patch_access_token(
    refresh_token: Annotated["JSONResponse", Depends(up_tokens_by_refresh)]
) -> "JSONResponse":
    """**Path access and refresh token**.

    Requirement :
        - Cookie:  `refresh_token`
    """
    return refresh_token


@auth.delete(
    path=AuthRoutes.LOGOUT_PATH,
    status_code=status.HTTP_200_OK,
    response_model=Status,
    responses=Response500.responses,
    dependencies=[
        Depends(HTTPBearer()),
        Depends(APIKeyCookie(name=JWT.TOKEN_TYPE_REFRESH)),
    ],
)
async def logout_user() -> "JSONResponse":
    """**Delete loging user**.

    Requirement :
        - Cookie:  `refresh_token`
        - Authorization: Bearer

    """
    response = JSONResponse(
        content=Status().model_dump(),
        status_code=status.HTTP_200_OK,
    )
    response.delete_cookie(key=JWT.TOKEN_TYPE_REFRESH)
    response.headers.update(Headers.WWW_AUTH_BEARER_LOGOUT)
    response.headers.update(Headers.AUTHORIZATION)
    return response
