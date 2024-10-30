"""Main module."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.core.controllers.auth import auth
from src.core.controllers.depends.utils.connect_db import disconnect_db
from src.core.controllers.depends.utils.redis_chash import (
    close_redis,
    init_redis,
)
from src.core.controllers.referral import ref
from src.core.controllers.registration import registration
from src.core.settings.constants import Prefix


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Connect and close DB."""
    redis = await init_redis()
    yield
    await disconnect_db()
    await close_redis(client=redis)


def create_app() -> FastAPI:
    """Maker FastAPI."""
    app_ = FastAPI(
        root_path=Prefix.API,
    )
    app_.include_router(router=registration)
    app_.include_router(router=auth)
    app_.include_router(router=ref)

    return app_


if __name__ == "__main__":
    """Local test"""
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info",
    )
