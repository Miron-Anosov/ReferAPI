"""DTO cache model."""

from typing import Any, Callable

from pydantic import BaseModel


class CacheDataDTO(BaseModel):
    """DTO cache model."""

    pref_key: str
    exp: int | float
    fun: Callable
    return_type_ob: Any
    id_pers: str | int | None
