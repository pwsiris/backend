import asyncio
from typing import Any

from common.config import cfg
from common.errors import HTTPabort
from db.common import get_model_dict
from db.models import SCHEMA, DataParams
from schemas import data_params as schema_data_params
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class DataParamsData:
    DEFAULTS = {
        "TIMECODE_MESSAGE": {"value_str": "Saved"},
        "SITE_MESSAGES_ENABLED": {"value_bool": False},
        "SITE_MESSAGES_TITLE_TEXT": {"value_str": ""},
        "SITE_MESSAGES_TITLE_EDITABLE": {"value_bool": False},
        "BITE_CHEAT_STREAMER_PERCENT": {"value_int": 0},
        "BITE_CHEAT_DEFENSE_PERCENT": {"value_int": 0},
        "MERCH_STATUS": {"value_str": ""},
    }

    def __init__(self) -> None:
        self.raw_data = {}
        self.data = {}
        self.lock = asyncio.Lock()

    def get_value(self, row_dict: dict[str, Any]) -> Any:
        for key, value in row_dict.items():
            if "value" in key and value != None:
                return value
        return None

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(DataParams))
            db_names = set()
            for row in db_data:
                db_names.add(row.name)
                self.raw_data[row.name] = get_model_dict(row)
                self.data[row.name] = self.get_value(self.raw_data[row.name])

            for name, value in self.DEFAULTS.items():
                if name not in db_names:
                    await session.execute(insert(DataParams).values(value))
                    self.raw_data[name] = value
                    self.data[name] = self.get_value(value)

        cfg.logger.info("Data Params info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{DataParams.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.raw_data = {}
            self.data = {}
            for name, value in self.DEFAULTS.items():
                await session.execute(insert(DataParams).values(value))
                self.raw_data[name] = value
                self.data[name] = self.get_value(value)

    async def add(
        self, session: AsyncSession, data_param: schema_data_params.Element
    ) -> None:
        async with self.lock:
            if data_param.name in self.data:
                HTTPabort(409, "Already exists")
            async with session.begin():
                await session.execute(
                    insert(DataParams).values(data_param.model_dump())
                )
                self.raw_data[data_param.name] = data_param.model_dump()
                self.data[data_param.name] = self.get_value(
                    self.raw_data[data_param.name]
                )

    async def update(
        self, session: AsyncSession, data_param: schema_data_params.Element
    ) -> None:
        async with self.lock:
            if data_param.name not in self.data:
                HTTPabort(404, "Not found")
            async with session.begin():
                await session.execute(
                    update(DataParams)
                    .where(DataParams.name == data_param.name)
                    .values(data_param.model_dump(exclude={"name"}))
                )
                self.raw_data[data_param.name] = data_param.model_dump()
                self.data[data_param.name] = self.get_value(
                    self.raw_data[data_param.name]
                )

    async def delete(self, session: AsyncSession, name: str) -> None:
        async with self.lock:
            if name in self.DEFAULTS:
                HTTPabort(409, "Can't remove params used in code")

            async with session.begin():
                await session.execute(delete(DataParams).where(DataParams.name == name))
                del self.data[name]
                del self.raw_data[name]

    def get(self, name: str) -> Any:
        return self.data.get(name)

    async def get_all(self, raw=False) -> list[dict[str, Any]]:
        async with self.lock:
            return [row for row in self.raw_data.values()]
