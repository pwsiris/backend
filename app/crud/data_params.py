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
                    row = {"name": name, **value}
                    await session.execute(insert(DataParams).values(row))
                    self.raw_data[name] = row
                    self.data[name] = self.get_value(row)

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
                row = {"name": name, **value}
                await session.execute(insert(DataParams).values(row))
                self.raw_data[name] = row
                self.data[name] = self.get_value(row)

    async def add(
        self, session: AsyncSession, elements: list[schema_data_params.Element]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_elements_count = 0
            inserted_ids = []
            for element in elements:
                if element.name in self.data:
                    inserted_ids.append(-1)
                    continue

                dicted_element = element.model_dump()
                async with session.begin():
                    inserted_element = await session.scalar(
                        insert(DataParams).values(dicted_element).returning(DataParams)
                    )
                    self.raw_data[element.name] = dicted_element
                    self.data[element.name] = self.get_value(dicted_element)

                    inserted_ids.append(inserted_element.id)
                    inserted_elements_count += 1
            if not inserted_elements_count:
                HTTPabort(409, "Elements already exist")
            return inserted_ids

    async def update(
        self, session: AsyncSession, elements: list[schema_data_params.Element]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            update_info = []
            for element in elements:
                if element.name not in self.data:
                    update_info.append("No element")
                    continue

                dicted_element = element.model_dump()
                async with session.begin():
                    await session.execute(
                        update(DataParams)
                        .where(DataParams.name == element.name)
                        .values(dicted_element)
                    )
                    self.raw_data[element.name] = dicted_element
                    self.data[element.name] = self.get_value(dicted_element)

                    update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            return update_info

    async def delete(
        self, session: AsyncSession, elements: list[schema_data_params.ElementName]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            delete_info = []
            for element in elements:
                if element.name not in self.data:
                    delete_info.append("False")
                    continue
                if element.name in self.DEFAULTS:
                    delete_info.append("Can't remove params used in code")
                    continue

                async with session.begin():
                    await session.execute(
                        delete(DataParams).where(DataParams.name == element.name)
                    )
                    del self.data[element.name]
                    del self.raw_data[element.name]

                    delete_info.append("True")
            if "True" not in delete_info:
                if "Can't remove params used in code" not in delete_info:
                    HTTPabort(404, "No elements to delete")
                if "False" not in delete_info:
                    HTTPabort(404, "Can't remove params used in code")
            return delete_info

    def get(self, name: str) -> Any:
        if name not in self.data:
            HTTPabort(404, "Data Param not found")
        return self.data.get(name)

    async def get_all(self, raw=False) -> list[dict[str, Any]]:
        async with self.lock:
            return [row for row in self.raw_data.values()]
