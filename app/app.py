from contextlib import asynccontextmanager

from api import routers
from common.all_data import all_data
from common.config import cfg
from common.errors import exception_handlers
from db.common import _engine, check_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan_function(FastAPP: FastAPI):
    await check_db()

    async with AsyncSession(_engine, expire_on_commit=False) as session:
        await all_data.setup(session)

    FastAPP.include_router(routers.routers, prefix="/api")

    yield

    await _engine.dispose()


app = FastAPI(
    title="PWSI",
    version="1.0.0",
    exception_handlers=exception_handlers,
    lifespan=lifespan_function,
    # openapi_url="/api/openapi.json",
    # docs_url="/api/docs",
    # redoc_url="/api/redoc",
)

if cfg.ENV == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*localhost:.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
