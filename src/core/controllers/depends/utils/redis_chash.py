"""Cache module for caching API responses with Redis."""

import json
from functools import update_wrapper, wraps
from typing import Any, Callable, Type

import pydantic
from fastapi import Request, Response
from fastapi.dependencies.utils import get_typed_return_annotation
from fastapi.responses import JSONResponse
from redis import asyncio as aioredis
from redis.asyncio.client import Redis
from starlette.status import HTTP_304_NOT_MODIFIED

from src.core.controllers.depends.utils.token_from import (
    get_user_id_from_token,
)
from src.core.settings.constants import Headers, Keys, TypeEncoding
from src.core.settings.env import settings
from src.core.validators.chach_dto import CacheDataDTO


def singleton(func: Callable) -> Callable:
    """Singleton pattern decorator for caching instances.

    Args:
        func (Callable): The function to wrap with singleton pattern.

    Returns:
        Callable: Wrapped function with singleton pattern.
    """
    instance: dict[str, Any] = {}

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        if ins_func := instance.get(func.__name__):
            return ins_func
        new_instance = await func(*args, **kwargs)
        instance[func.__name__] = new_instance
        return new_instance

    return wrapper


@singleton
async def setup_redis(
    url: str = settings.redis.redis_url,
    encoding: str = TypeEncoding.UTF8,
    decode_responses: bool = True,
) -> Redis:
    """Initialize Redis client.

    Args:
        url (str): Redis connection URL.
        encoding (str): Character encoding used for responses.
        decode_responses (bool): Flag for decoding responses.

    Returns:
        Redis: Redis client instance.
    """
    try:
        return await aioredis.from_url(
            url=url,
            encoding=encoding,
            decode_responses=decode_responses,
        )
    except aioredis.RedisError as e:
        raise e


async def close_redis(client: Redis) -> None:
    """Close the Redis connection.

    Args:
        client (Redis): Redis client instance to close.

    Raises:
        RedisError: If closing the connection fails.
    """
    try:
        await client.close()
    except aioredis.RedisError as e:
        raise e


async def init_redis() -> Redis:
    """Return initialized Redis client.

    Returns:
        Redis: Initialized Redis client.
    """
    return await setup_redis()


def serialize_data(data: Any) -> str:
    """Convert Pydantic model to JSON string.

    Args:
        data (pydantic.BaseModel): Data model to serialize.

    Returns:
        str: Serialized JSON string of the model.
    """
    try:
        if isinstance(data, pydantic.BaseModel):
            return data.model_dump_json()

        if isinstance(data, dict):
            return json.dumps(data)

        if isinstance(data, JSONResponse):
            return json.dumps(str(data.body))

        raise pydantic.ValidationError

    except pydantic.ValidationError as e:
        raise e


def deserialize_data(data: Any, return_type: Type[pydantic.BaseModel]) -> Any:
    """Convert JSON string to Pydantic model.

    Args:
        data (str): JSON string to deserialize.
        return_type (Type[pydantic.BaseModel]): Target model type.

    Returns:
        pydantic.BaseModel: Deserialized data model.
    """
    try:
        if isinstance(data, str):
            return return_type(**json.loads(data))
        if isinstance(data, pydantic.BaseModel):
            return return_type(**data.model_dump())

        raise pydantic.ValidationError

    except pydantic.ValidationError as e:
        raise e


def gen_key(
    prefix_key: str,
    id_user: str | int | None,
) -> str:
    """Generate cache key from request parameters.

    Args:
        prefix_key (str): Prefix for cache key.
        id_user (str): User ID.

    Returns:
        str: Generated cache key.
    """
    keys = [prefix_key]
    if id_user:
        keys.append(str(id_user))
    return ":".join(keys)


def gen_etag(cached_value: str) -> str:
    """Generate ETag from cached value.

    Args:
        cached_value (str): Cached data string.

    Returns:
        str: Weak ETag generated from cached value.
    """
    return f"W/{hash(cached_value)}"


def set_response_headers(
    response: Response,
    exp: int | float,
    cached_value: str,
    update: bool = False,
):
    """Set cache headers in the response.

    Args:
        response (Response): HTTP response object.
        exp (int): Expiration time in seconds.
        cached_value (str): Cached data string for ETag.
        update (bool): Whether cache is a hit or miss.
    """
    response.headers[Headers.CACHE_CONTROL] = f"{Headers.CACHE_MAX_AGE}{exp}"
    response.headers[Headers.ETAG] = gen_etag(cached_value)
    response.headers[Headers.X_CACHE] = (
        Headers.X_CACHE_MISS if update is False else Headers.X_CACHE_HIT
    )


def check_etag(request: Request, response: Response) -> bool:
    """Validate ETag to check cache validity.

    Args:
        request (Request): Incoming request with ETag.
        response (Response): Response containing ETag.

    Returns:
        bool: True if ETag matches, False otherwise.
    """
    return request.headers.get(Headers.IF_NONE_MATCH) == response.headers.get(
        Headers.ETAG
    )


async def get_cache(cache_key: str) -> str | None:
    """Retrieve cached data from Redis by key.

    Args:
        cache_key (str): Key to retrieve data from Redis.

    Returns:
        str | None: Cached data if available, else None.
    """
    redis_client: Redis = await setup_redis()
    try:
        return await redis_client.get(cache_key)
    except aioredis.RedisError as e:
        raise e


async def del_cache(cache_key: str) -> None:
    """Delete cached data from Redis by key.

    Args:
        cache_key (str): Key to delete from Redis.

    Raises:
        RedisError: If deletion fails.
    """
    redis_client: Redis = await setup_redis()
    try:
        return await redis_client.delete(cache_key)
    except aioredis.RedisError as e:
        raise e


async def set_cache(cache_key, value, ex) -> None:
    """Store data in Redis with expiration time.

    Args:
        cache_key (str): Key to store data under.
        value (Any): Data to store in Redis.
        ex (int): Expiration time in seconds.

    Raises:
        RedisError: If storage fails.
    """
    redis_client: Redis = await setup_redis()
    try:
        await redis_client.set(
            name=cache_key,
            value=value,
            ex=ex,
        )
    except aioredis.RedisError as e:
        raise e


async def select_request_and_response(**kwargs) -> tuple[Request, Response]:
    """Select request and response from keyword arguments.

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        tuple[Request, Response]: Selected request and response objects.
    """
    request: Request = kwargs.get(Keys.REQUEST)
    response: Response = kwargs.get(Keys.RESPONSE)
    return request, response


def cache_http_get(expire: int, prefix_key: str) -> Callable:
    """Cache decorator for GET requests.

    Caches the response of GET requests using Redis. Only applies to
    requests with the GET method.

    Args:
        expire (int): Expiration time for cached data in seconds.
        prefix_key (str): Prefix to generate the cache key.

    Returns:
        Callable: Decorator function that wraps the original function.
    """

    def _decorator(function: Callable) -> Callable:
        return_type = get_typed_return_annotation(function)

        @wraps(function)
        async def _wrapper(*args: Any, **kwargs: Any):
            request, response = await select_request_and_response(**kwargs)

            if request.method == Keys.GET:
                chash_dto = CacheDataDTO(
                    pref_key=prefix_key,
                    exp=expire,
                    fun=function,
                    return_type_ob=return_type,
                )
                await core_chash_decorator(
                    chash_dto,
                    *args,
                    **kwargs,
                )
            else:
                return await function(*args, **kwargs)

        update_wrapper(_wrapper, function)
        return _wrapper

    return _decorator


def cache_http_singleton_value_by_user(
    expire: int | float, prefix_key: str
) -> Callable:
    """Cache decorator for singleton token operations.

    Caches a singleton token for POST or DELETE requests. On DELETE,
    clears the token cache. On POST, caches the token response.

    Args:
        expire (int): Expiration time for cached data in seconds.
        prefix_key (str): Prefix to generate the cache key.

    Returns:
        Callable: Decorator function that wraps the original function.
    """

    def _decorator(func: Callable) -> Callable:
        return_type = get_typed_return_annotation(func)

        @wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any):
            request, response = await select_request_and_response(**kwargs)
            user_id = get_user_id_from_token(request)
            if request.method == Keys.DELETE:
                token_key = gen_key(
                    prefix_key=prefix_key,
                    id_user=user_id,
                )
                await del_cache(cache_key=token_key)
                return True

            elif request.method == Keys.POST:
                chash_dto = CacheDataDTO(
                    pref_key=prefix_key,
                    exp=expire,
                    fun=func,
                    return_type_ob=return_type,
                    id_pers=user_id,
                )
                return await core_chash_decorator(
                    chash_dto,
                    *args,
                    **kwargs,
                )
            else:
                return await func(*args, **kwargs)

        update_wrapper(_wrapper, func)
        return _wrapper

    return _decorator


async def core_chash_decorator(
    chash_dto: CacheDataDTO,
    *args,
    **kwargs,
) -> Callable:
    """Core decorator for caching responses.

    Handles the core caching mechanism: retrieves, sets, and validates
    cached responses for specified requests.

    Args:
        chash_dto: CacheDataDTO

    Returns:
        Callable: JSON response with cached or fresh data.
    """
    request, response = await select_request_and_response(**kwargs)

    cache_key = gen_key(
        prefix_key=chash_dto.pref_key, id_user=chash_dto.id_pers
    )

    cached_value = await get_cache(cache_key=cache_key)

    if cached_value is None:
        data_response = await chash_dto.fun(*args, **kwargs)
        cached_value = serialize_data(data_response)
        await set_cache(
            cache_key=cache_key, value=cached_value, ex=chash_dto.exp
        )
        set_response_headers(response, chash_dto.exp, cached_value)

    else:
        set_response_headers(
            response=response,
            exp=chash_dto.exp,
            cached_value=cached_value,
            update=True,
        )
        if check_etag(request=request, response=response):
            return Response(status_code=HTTP_304_NOT_MODIFIED)

        data_response = deserialize_data(
            cached_value, chash_dto.return_type_ob
        )

    return data_response


async def is_alive_referral_token_in_chash(
    prefix_key: str,
    referral_owner_id: str,
) -> str | None:
    """Check if referral token exists in cache.

    Verifies the existence of a referral token in Redis using the
    generated cache key.

    Args:
        prefix_key (str): Prefix for the cache key.
        referral_owner_id (str): Identifier for the referral owner.

    Returns:
        bool: True if the token exists in cache, False otherwise.
    """
    token_key = gen_key(
        prefix_key=prefix_key,
        id_user=referral_owner_id,
    )
    cached_token = await get_cache(cache_key=token_key)
    return cached_token if cached_token else None
