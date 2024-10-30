"""Common Raise HTTPException."""

import uuid
from typing import Optional

from fastapi import HTTPException, status

from src.core.settings.constants import Headers, MessageError
from src.core.validators.error import ErrorMessage


def http_exception(
    status_code: int,
    error_type: str,
    error_message: str,
    headers: dict[str, str] | None = None,
) -> HTTPException:
    """Return HTTPException.

    Args:
        - status_code (int): HTTP status.
        - error_type (str): Type error.
        - error_message (str): Message error.
        - headers (dict[str, str] | None): If it is requirement.
    Raise:
        - HTTPException

    """
    return HTTPException(
        status_code=status_code,
        detail=ErrorMessage(
            error_type=error_type,
            error_message=error_message,
        ).model_dump(),
        headers=headers,
    )


def valid_id_or_error_422(id_data: str):
    """Validate the given UUID.

    Args:
        id_data (str): The identifier as a string.

    Raises:
        HTTPException: If `request_id` is invalid,
        raises HTTP 422 with an error message.
    """
    try:
        uuid.UUID(id_data, version=4)
    except ValueError:
        raise http_exception(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type=MessageError.INVALID_ID_ERR,
            error_message=MessageError.INVALID_ID_ERR_MESSAGE,
        )


def valid_password_or_error_422(pwd: str, pwd2: str) -> None:
    """Check the given password.

    Args:
        pwd (str): The password as a string.
        pwd2 (str): The control password as a string.

    Raises:
        HTTPException: If `pwd` is not same as `pwd2`.,
        raises HTTP 422 with an error message.
    """
    try:
        if pwd != pwd2:
            raise ValueError
    except ValueError:
        raise http_exception(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type=MessageError.INVALID_ID_ERR,
            error_message=MessageError.INVALID_ID_ERR_MESSAGE,
        )


def raise_http_404(
    error_type: str = MessageError.INVALID_ID_ERR,
    error_message: str = MessageError.INVALID_ID_ERR_MESSAGE_404,
    status_code: int = status.HTTP_404_NOT_FOUND,
):
    """Raise an HTTP 404 exception with a specified error message and type.

    Args:
        error_type (str): The type of the error to raise. Defaults to
            `MessageError.INVALID_ID_ERR`.
        error_message (str): The error message to display. Defaults to
            `MessageError.INVALID_ID_ERR_MESSAGE_404`.
        status_code (int): The HTTP status code to return. Defaults to
            `status.HTTP_404_NOT_FOUND`.

    Raises:
        HTTPException: Raises an HTTP 404 exception with the specified
            details.
    """
    raise http_exception(
        status_code=status_code,
        error_type=error_type,
        error_message=error_message,
    )


def raise_hht_401(
    status_code: int = status.HTTP_401_UNAUTHORIZED,
    error_type: str = MessageError.TYPE_ERROR_INVALID_AUTH,
    error_message: str = MessageError.INVALID_EMAIL_OR_PWD,
    headers: dict = Headers.WWW_AUTH_BEARER,
):
    """Raise HTTP 401 error with customizable parameters.

    Args:
        status_code (int): HTTP status code for unauthorized error.
        error_type (str): Type of authentication error.
        error_message (str): Error message for invalid credentials.
        headers (dict): Auth header type, default is Bearer.
    """
    raise http_exception(
        status_code=status_code,
        error_type=error_type,
        error_message=error_message,
        headers=headers,
    )


def raise_400_bad_req(
    status_code=status.HTTP_400_BAD_REQUEST,
    error_type=MessageError.TYPE_ERROR_INVALID_REG,
    error_message=MessageError.MESSAGE_IF_EMAIL_ALREADY_EXIST,
):
    """Raise error for failed registration."""
    raise http_exception(
        status_code=status_code,
        error_type=error_type,
        error_message=error_message,
    )
