from contextlib import asynccontextmanager

from api import routers
from common.all_data import all_data
from common.config import cfg
from common.errors import exception_handlers
from common.utils import get_logger, levelDEBUG, levelINFO
from db.common import _engine, check_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(levelDEBUG if cfg.ENV == "dev" else levelINFO)


@asynccontextmanager
async def lifespan_function(FastAPP: FastAPI):
    await check_db(logger)

    async with AsyncSession(_engine, expire_on_commit=False) as session:
        await all_data.SAVE_CHOICES.setup(session)

        await all_data.BITE_IGNORE_LIST.setup(session)
        await all_data.BITE_ACTIONS.setup(session)
        await all_data.BITE_PLACES.setup(session)
        await all_data.BITE_BODY_PARTS.setup(session)

        await all_data.COUNTER.setup(session)
        await all_data.COUNTER_DEATH.setup(session)
        await all_data.COUNTER_GLOBAL.setup(session)

        await all_data.ANIME.setup(session)
        await all_data.CHALLENGES.setup(session)
        await all_data.GAMES.setup(session)
        await all_data.LORE.setup(session)
        await all_data.MARATHONS.setup(session)
        await all_data.ROULETTE.setup(session)
        await all_data.SOCIALS.setup(session)

    FastAPP.include_router(routers.routers, prefix="/api")

    if cfg.ENV == "dev":
        FastAPP.add_middleware(
            CORSMiddleware,
            allow_origin_regex=".*localhost:.*",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    yield

    await _engine.dispose()


FastAPP = FastAPI(
    title="PWSI",
    version="1.0.0",
    exception_handlers=exception_handlers,
    lifespan=lifespan_function,
    # openapi_url="/api/openapi.json",
    # docs_url="/api/docs",
    # redoc_url="/api/redoc",
)
