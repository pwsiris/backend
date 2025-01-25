import asyncio
import re
from datetime import date as ddate
from datetime import datetime
from datetime import time as dtime

from common.config import cfg
from common.errors import HTTPabort
from db.common import get_model_dict
from db.models import SCHEMA, RouletteAwards
from fastapi.encoders import jsonable_encoder
from schemas import roulette as schema_roulette
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class RouletteData:
    def __init__(self) -> None:
        self.data = {}
        self.awards = set()
        self.rarities = []
        self.sorted_list = []
        self.descriptions = []
        self.lock = asyncio.Lock()

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(RouletteAwards))
            for row in db_data:
                self.data[row.id] = get_model_dict(row)
                self.awards.add(row.name)
        self.resort()
        cfg.logger.info("Roulette info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{RouletteAwards.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.awards = set()
            self.sorted_list = []
            self.descriptions = []

    def resort(self) -> None:
        rarities = set()
        for award in self.data.values():
            rarities.add(award["rarity"])

        self.rarities = sorted(
            list(rarities),
            key=lambda item: -float(
                re.search("\\((.+?)\\%\\)", item).group(1).replace(",", ".")
            ),
        )

        self.sorted_list = sorted(self.data.values(), key=lambda award: award["name"])

        descriptions = []
        for award in self.sorted_list:
            if award["description"]:
                try:
                    index = descriptions.index(award["description"])
                except Exception:
                    descriptions.append(award["description"])
                    index = len(descriptions)
                award["description_index"] = index
        self.descriptions = descriptions

    async def add(
        self, session: AsyncSession, elements: list[schema_roulette.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_elements_count = 0
            inserted_ids = []
            for element in elements:
                if element.name in self.awards:
                    inserted_ids.append(-1)
                    continue

                async with session.begin():
                    dicted_element = element.model_dump()

                    new_award = RouletteAwards(**dicted_element)
                    session.add(new_award)
                    await session.flush()
                    await session.refresh(new_award)

                    dicted_element["id"] = new_award.id
                    self.data[new_award.id] = dicted_element
                    self.awards.add(element.name)

                    inserted_ids.append(new_award.id)
                    inserted_elements_count += 1
            if not inserted_elements_count:
                HTTPabort(409, "Elements already exist")
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_roulette.DeletedElement]
    ) -> list[bool]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            delete_info = []
            for element in elements:
                if element.id not in self.data:
                    delete_info.append(False)
                    continue

                async with session.begin():
                    await session.execute(
                        delete(RouletteAwards).where(RouletteAwards.id == element.id)
                    )
                    self.awards.remove(self.data[element.id]["name"])
                    del self.data[element.id]
                    delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_roulette.UpdatedElement]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            update_info = []
            for element in elements:
                if element.id not in self.data:
                    update_info.append("No element")
                    continue
                dicted_element = element.model_dump(exclude={"id"}, exclude_none=True)
                if dicted_element.get("name") in self.awards:
                    update_info.append("New name not unique")
                    continue
                async with session.begin():
                    await session.execute(
                        update(RouletteAwards)
                        .where(RouletteAwards.id == element.id)
                        .values(dicted_element)
                    )
                if "name" in dicted_element:
                    self.awards.remove(self.data[element.id]["name"])
                    self.awards.add(dicted_element["name"])
                self.data[element.id].update(dicted_element)
                update_info.append("Updated")
            if "Updated" not in update_info:
                if "New name not unique" not in update_info:
                    HTTPabort(404, "No elements to update")
                if "No element" not in update_info:
                    HTTPabort(409, "No new unique names")
            self.resort()
            return update_info

    async def get_all(self, raw: bool) -> list[dict]:
        if raw:
            async with self.lock:
                result = []
                for item in self.data.values():
                    item_record = {}
                    for tag in ("id", "name", "rarity", "description"):
                        if item[tag]:
                            item_record[tag] = item[tag]
                    result.append(item_record)

                return jsonable_encoder(
                    result,
                    custom_encoder={
                        datetime: lambda datetime_obj: (
                            datetime_obj.isoformat()
                        ).replace("T", " "),
                        ddate: lambda date_obj: (date_obj.isoformat()),
                        dtime: lambda time_obj: (time_obj.isoformat()),
                    },
                )
        return {
            "rarities": self.rarities,
            "awards": self.sorted_list,
            "descriptions": self.descriptions,
        }
