from argparse import ArgumentParser
from contextlib import asynccontextmanager

import uvicorn
from common.config import cfg
from common.errors import exception_handlers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

parser = ArgumentParser(description="PWSI backend")
parser.add_argument(
    "--host",
    "-H",
    action="store",
    dest="host",
    default="0.0.0.0",
    help="Host addr",
)
parser.add_argument(
    "--port",
    "-P",
    action="store",
    dest="port",
    default="8040",
    help="Port",
)
parser.add_argument(
    "--env",
    "-E",
    action="store",
    dest="env",
    default="dev",
    help="Running environment",
)
args = parser.parse_args()
CURRENT_ENV = args.env


@asynccontextmanager
async def lifespan_function(FastAPP: FastAPI):
    await cfg.get_creds(CURRENT_ENV)
    print("INFO:\t  Config was loaded")
    await cfg.get_secrets(True)
    print("INFO:\t  Secrets were loaded to config")

    from common.all_data import all_data
    from db.utils import _engine, check_db

    await check_db()
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
        await all_data.SOCIALS.setup(session)

    from api import routers

    FastAPP.include_router(routers.routers, prefix="/api")

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

if CURRENT_ENV == "dev":
    FastAPP.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*localhost:.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s - %(client_addr)s - '%(request_line)s' %(status_code)s"

    uvicorn.run(
        "main:FastAPP",
        host=args.host,
        port=int(args.port),
        proxy_headers=True,
        log_config=log_config,
        reload=(True if CURRENT_ENV == "dev" else False),
    )
