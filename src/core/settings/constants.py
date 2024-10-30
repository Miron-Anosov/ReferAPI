"""API constants."""

from pathlib import Path
from typing import Collection

from fastapi import status


class Prefix:
    """Prefix."""

    API = "/api"


class AuthRoutes:
    """Authorization routes."""

    TAG = "AUTH"
    LOGIN_PATH = "/auth/login"
    LOGOUT_PATH = "/auth/logout"
    TOKEN_PATH = "/auth/token"


class UserRefRoutes:
    """Registration routes."""

    TAG = "USER"
    CREATE_USER_PATH = "/user/new"
    REFERRAL_POST_PATH = "/user/referral"
    REFERRAL_TOKEN_GET_PATH_BY_EMAIL = "/user/referral/email"
    REFERRAL_GET_PATH_BY_ID = "/user/referral"
    REFERRAL_DELETE_PATH = "/user/referral"


class DetailError:
    """Default Error model to response."""

    CONTENT = {
        "application/json": {
            "example": {
                "detail": {
                    "result": False,
                    "error_type": "String",
                    "error_message": "String",
                }
            }
        }
    }


class ResponseError:
    """Swagger Docs Errors."""

    RESPONSES = {
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Not authenticated",
            "content": DetailError.CONTENT,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden",
            "content": DetailError.CONTENT,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
            "content": DetailError.CONTENT,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation Error",
            "content": DetailError.CONTENT,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Invalid credentials",
            "content": DetailError.CONTENT,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request",
            "content": DetailError.CONTENT,
        },
    }


class ResponsesAuthUser:
    """Swagger Docs."""

    responses = dict()
    responses[status.HTTP_401_UNAUTHORIZED] = ResponseError.RESPONSES.get(
        status.HTTP_401_UNAUTHORIZED
    )
    responses[status.HTTP_500_INTERNAL_SERVER_ERROR] = (
        ResponseError.RESPONSES.get(status.HTTP_500_INTERNAL_SERVER_ERROR)
    )


class HTTPResponseNewUser:
    """Swagger Docs."""

    responses = dict()
    responses[status.HTTP_500_INTERNAL_SERVER_ERROR] = (
        ResponseError.RESPONSES.get(status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    responses[status.HTTP_422_UNPROCESSABLE_ENTITY] = (
        ResponseError.RESPONSES.get(status.HTTP_422_UNPROCESSABLE_ENTITY)
    )
    responses[status.HTTP_404_NOT_FOUND] = ResponseError.RESPONSES.get(
        status.HTTP_404_NOT_FOUND
    )
    responses[status.HTTP_400_BAD_REQUEST] = ResponseError.RESPONSES.get(
        status.HTTP_400_BAD_REQUEST
    )


class HTTPResponseGETReferrals(HTTPResponseNewUser):
    """Swagger Docs."""


class ResponsesGetRef:
    """Swagger Docs Get Tweets."""

    responses_304: dict[str, Collection[str]] | None = {
        status.HTTP_304_NOT_MODIFIED: {
            "description": "Not Modified",
            "content": {},
        },
    }

    responses = dict()
    responses[status.HTTP_500_INTERNAL_SERVER_ERROR] = (
        ResponseError.RESPONSES.get(status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    responses[status.HTTP_304_NOT_MODIFIED] = responses_304
    responses[status.HTTP_404_NOT_FOUND] = ResponseError.RESPONSES.get(
        status.HTTP_404_NOT_FOUND
    )
    responses[status.HTTP_422_UNPROCESSABLE_ENTITY] = (
        ResponseError.RESPONSES.get(status.HTTP_422_UNPROCESSABLE_ENTITY)
    )


class Response500:
    """Swagger Docs."""

    responses = dict()
    responses[status.HTTP_500_INTERNAL_SERVER_ERROR] = (
        ResponseError.RESPONSES.get(status.HTTP_500_INTERNAL_SERVER_ERROR)
    )


class MimeTypes:
    """МIME types constants."""

    APPLICATION_JSON = "application/json"


class JWT:
    """STATIC JWT DATA."""

    DESCRIPTION_PYDANTIC_ACCESS_TOKEN = (
        "Authorization: Bearer JWT access-token. It'll set at "
    )
    DESCRIPTION_PYDANTIC_REFRESH_TOKEN = "Set-cookie: JWT refresh_token"
    DESCRIPTION_PYDANTIC_TOKEN_TYPE = "Bearer"
    DESCRIPTION_PYDANTIC_TITLE = "Token"
    DESCRIPTION_PYDANTIC_EXPIRE_REFRESH = "expires_refresh"
    PAYLOAD_EXPIRE_KEY = "exp"
    PAYLOAD_IAT_KEY = "iat"
    PAYLOAD_SUB_KEY = "sub"
    PAYLOAD_USERNAME_KEY = "username"
    PAYLOAD_REFERRAL_KEY = "singleton_token"
    TOKEN_TYPE_FIELD = "type"
    TOKEN_TYPE_ACCESS = "access_token"
    TOKEN_TYPE_REFRESH = "refresh_token"
    TOKEN_TYPE_REFERRAL = "referral_token"
    PREFIX_BY_EMAIL_OR_ID = "referral_token_by_email_or_id"
    EXP_BY_EMAIL_OR_ID = 10


class CommonConfSettings:
    """Common configurate."""

    ENV_FILE_NAME = ".env"
    EXTRA_IGNORE = "ignore"

    ENV = Path(__file__).parent.parent.parent.parent / ENV_FILE_NAME


class DBconf:
    """Conf for settings."""

    DB_HOST = "0.0.1"
    DB_PORT = 5432
    DB_USER = "default"
    DB_PASSWORD = "secret"
    DB_NAME = "referral"


class JWTconf:
    """Conf for settings."""

    ALGORITHM = "RS256"
    ENV_PREFIX = "JWT_"
    ACCESS_EXPIRE_MINUTES = 15
    REFRESH_EXPIRE_DAYS = 30
    REFERRAL_EXPIRE_DAYS = 100
    PRIVATE_KEY = "private_key"
    PUBLIC_KEY = "public_key"


class GunicornConf:
    """Gunicorn conf data."""

    BUILD = "unix:/tmp/gunicorn.sock"
    WSGI_APP = "src.main:create_app()"
    WORKER_CLASS = "uvicorn.workers.UvicornWorker"
    LOG_LEVEL_DEFAULT = "warning"
    ACCESSLOG = "-"
    ERRORLOG = "-"
    TIMEOUT_DEFAULT = 60
    MIN_WORKERS = 1


class RedisConf:
    """Redis conf data."""

    PREFIX = "referral_api"
    MIN_LENGTH_PREFIX = 3
    HOST = "redis"
    DEFAULT_PORT = 6379
    REDIS_DB = 0
    REDIS_USER = "default"
    PASSWORD = "secret"


class MessageError:
    """STATIC ERROR DATA."""

    INVALID_EMAIL_OR_PWD = "Invalid email or password"
    INVALID_TOKEN_ERR = "Invalid token."
    INVALID_ID_ERR = "Invalid ID."
    INVALID_ID_ERR_MESSAGE = "Type ID is not correct."
    INVALID_ID_ERR_MESSAGE_404 = "ID is not exist."
    INVALID_TOKEN_ERR_MESSAGE = "Please repeat authentication."
    INVALID_REF_TOKEN_ERR_MESSAGE = "Token is not exist."
    TYPE_ERROR_INVALID_AUTH = "Invalid auth."
    TYPE_ERROR_INVALID_REG = "Invalid registration."
    TYPE_ERROR_INTERNAL_SERVER_ERROR = "Internal server error."
    TYPE_ERROR_404 = "HTTP_404_NOT_FOUND"
    TYPE_ERROR_500 = "HTTP_500_INTERNAL_SERVER_ERROR"
    MESSAGE_SERVER_ERROR = "An error occurred."
    MESSAGE_ENV_FILE_INCORRECT_OR_NOT_EXIST = "~/.env  incorrect or not exist"
    MESSAGE_NO_REFERRALS_FOUND = "No referrals found"
    MESSAGE_USER_NOT_FOUND = "User not found"
    MESSAGE_IF_EMAIL_ALREADY_EXIST = (
        "Registration failed. Please check your information."
    )


class Headers:
    """STATIC HEADERS DATA."""

    WWW_AUTH_BEARER = {"WWW-Authenticate": "Bearer"}
    WWW_AUTH_BEARER_LOGOUT = {"WWW-Authenticate": 'Bearer realm="logout"'}
    AUTHORIZATION = {"Authorization": ""}
    WWW_AUTH_BEARER_EXPIRED = {
        "WWW-Authenticate": 'Bearer realm="Refresh token expired"'
    }
    CACHE_CONTROL = "Cache-Control"
    CACHE_MAX_AGE = "max-age="
    ETAG = "ETag"
    X_CACHE = "X-Cache"
    X_CACHE_MISS = "MISS"
    X_CACHE_HIT = "HIT"
    IF_NONE_MATCH = "if-none-match"


class Keys:
    """KEYS."""

    REQUEST = "request"
    RESPONSE = "response"
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    AUTH_HEADER = "authorization"
    AUTH_HEADER_PREF_BEARER = 7


class TypeEncoding:
    """STATIC ENCODING DATA."""

    UTF8 = "utf-8"
