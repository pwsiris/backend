from common.config import cfg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text

_engine = create_async_engine(cfg.DB_CONNECTION_STRING)


async def get_session() -> AsyncSession:
    async with AsyncSession(_engine, expire_on_commit=False) as session:
        yield session


async def check_db() -> None:
    try:
        async with AsyncSession(_engine, expire_on_commit=False) as session:
            answer = await session.execute(text("SELECT version();"))
            print(
                f"INFO:\t  Successfully connecting to database.\n\t  {answer.first()}",
                flush=True,
            )
    except Exception as e:
        print(f"ERROR:\t  Failed to connect to database:\n{str(e)}", flush=True)
        raise
