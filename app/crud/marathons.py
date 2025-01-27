import asyncio
from copy import deepcopy
from datetime import date as ddate
from datetime import datetime
from datetime import time as dtime

import httpx
from common.config import cfg
from common.errors import HTTPabort
from db.common import get_model_dict
from db.models import SCHEMA, Marathons
from fastapi.encoders import jsonable_encoder
from schemas import marathons as schema_marathons
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class MarathonsData:
    def __init__(self) -> None:
        self.data = {}
        self.sorted_list = []
        self.lock = asyncio.Lock()

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Marathons))
            for row in db_data:
                self.data[row.id] = get_model_dict(row)
        self.resort()
        cfg.logger.info("Marathons info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Marathons.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.sorted_list = []

    def resort(self) -> None:
        marathons_entities = sorted(
            self.data.values(), key=lambda marathon_entity: marathon_entity["order"]
        )
        marathons = {}
        for marathon_entity in marathons_entities:
            marathon_entity_copy = deepcopy(marathon_entity)
            if marathon_entity_copy["date_start"]:
                marathon_entity_copy["date_start"] = marathon_entity_copy[
                    "date_start"
                ].isoformat()
            if marathon_entity_copy["date_end"]:
                marathon_entity_copy["date_end"] = marathon_entity_copy[
                    "date_end"
                ].isoformat()

            id = marathon_entity["id"]
            m_id = marathon_entity["marathon_id"]
            if m_id:
                if m_id not in marathons:
                    marathons[m_id] = {"list": []}
                marathons[m_id]["list"].append(deepcopy(marathon_entity_copy))
            else:
                if id in marathons:
                    marathons[id].update(marathon_entity_copy)
                else:
                    marathon = deepcopy(marathon_entity_copy)
                    marathon["list"] = []
                    marathons[id] = marathon

        for marathon_id in marathons:
            try:
                if marathons[marathon_id]["list"][-1]["status"] in (
                    "Пройдено",
                    "Завершено",
                    "Выполнено",
                    "Отложено",
                    "Заброшено",
                ):
                    marathons[marathon_id]["status"] = "Завершено"
                elif marathons[marathon_id]["list"][0]["status"] != None:
                    marathons[marathon_id]["status"] = "В процессе"
            except Exception:
                pass

        self.sorted_list = sorted(
            marathons.values(), key=lambda marathon: marathon["order"]
        )

    async def check_steam(self, steam_id: int | None) -> dict:
        result = {}
        if steam_id:
            result["link"] = f"https://store.steampowered.com/app/{steam_id}"
            try:
                templates = [
                    f"https://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/capsule_616x353.jpg",
                    f"https://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/header.jpg",
                    f"https://cdn.cloudflare.steamstatic.com/steam/apps/{steam_id}/header.jpg",
                    f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{steam_id}/header.jpg",
                ]
                for template in templates:
                    async with httpx.AsyncClient() as ac:
                        response = await ac.get(template)
                        if response.status_code == 200:
                            result["picture"] = template
                            break
                if not result.get("picture"):
                    cfg.logger.warning(f"No valid pic for steam-game {steam_id}")
            except Exception:
                cfg.logger.warning(f"Error getting steam-game {steam_id} pic")
        return result

    async def add(
        self, session: AsyncSession, elements: list[schema_marathons.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_ids = []
            for element in elements:
                if element.marathon_id:
                    if element.marathon_id not in self.data:
                        inserted_ids.append(-1)
                        continue
                if element.order:
                    marathon_entities = []
                    for marathon_entity_id in self.data:
                        if (
                            self.data[marathon_entity_id]["marathon_id"]
                            == element.marathon_id
                        ):
                            marathon_entities.append(
                                {
                                    "id": marathon_entity_id,
                                    "order": self.data[marathon_entity_id]["order"],
                                }
                            )
                    if 1 <= element.order <= len(marathon_entities):
                        async with session.begin():
                            await session.execute(
                                update(Marathons)
                                .where(
                                    Marathons.marathon_id == element.marathon_id,
                                    Marathons.order >= element.order,
                                )
                                .values(order=Marathons.order + 1)
                            )
                            for marathon_entity_id in self.data:
                                if (
                                    self.data[marathon_entity_id]["marathon_id"]
                                    == element.marathon_id
                                    and self.data[marathon_entity_id]["order"]
                                    >= element.order
                                ):
                                    self.data[marathon_entity_id]["order"] += 1
                    else:
                        element.order = len(marathon_entities) + 1
                else:
                    element.order = len(marathon_entities) + 1

                additional_info = await self.check_steam(element.steam_id)
                async with session.begin():
                    dicted_element = element.model_dump()

                    if not dicted_element["link"]:
                        dicted_element["link"] = additional_info.get("link")
                    if not dicted_element["picture"]:
                        dicted_element["picture"] = additional_info.get("picture")

                    new_marathon_entity = Marathons(**dicted_element)
                    session.add(new_marathon_entity)
                    await session.flush()
                    await session.refresh(new_marathon_entity)

                    dicted_element["id"] = new_marathon_entity.id
                    self.data[new_marathon_entity.id] = dicted_element

                    inserted_ids.append(new_marathon_entity.id)
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_marathons.DeletedElement]
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
                        delete(Marathons).where(Marathons.id == element.id)
                    )
                    await session.execute(
                        delete(Marathons).where(Marathons.marathon_id == element.id)
                    )
                    await session.execute(
                        update(Marathons)
                        .where(
                            Marathons.marathon_id
                            == self.data[element.id]["marathon_id"],
                            Marathons.order > self.data[element.id]["order"],
                        )
                        .values(order=Marathons.order - 1)
                    )
                    for marathon_entity_id in self.data:
                        if (
                            self.data[marathon_entity_id]["marathon_id"]
                            == self.data[element.id]["marathon_id"]
                            and self.data[marathon_entity_id]["order"]
                            > self.data[element.id]["order"]
                        ):
                            self.data[marathon_entity_id]["order"] -= 1
                    del self.data[element.id]
                    delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_marathons.UpdatedElement]
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

                new_marathon_id = dicted_element.get("marathon_id")
                if new_marathon_id != None:
                    await session.execute(
                        update(Marathons)
                        .where(
                            Marathons.marathon_id
                            == self.data[element.id]["marathon_id"],
                            Marathons.order > self.data[element.id]["order"],
                        )
                        .values(order=Marathons.order - 1)
                    )
                    new_element_position = 1
                    for marathon_entity_id in self.data:
                        if (
                            self.data[marathon_entity_id]["marathon_id"]
                            == self.data[element.id]["marathon_id"]
                            and self.data[marathon_entity_id]["order"]
                            > self.data[element.id]["order"]
                        ):
                            self.data[marathon_entity_id]["order"] -= 1
                        if self.data[marathon_entity_id] == new_marathon_id:
                            new_element_position += 1

                    await session.execute(
                        update(Marathons)
                        .where(Marathons.id == element.id)
                        .values(order=new_element_position)
                    )
                    self.data[element.id]["order"] = new_element_position

                if dicted_element.get("order") != None:
                    marathon_entities = []
                    for marathon_entity_id in self.data:
                        if (
                            self.data[marathon_entity_id]["marathon_id"]
                            == self.data[element.id]["marathon_id"]
                        ):
                            marathon_entities.append(
                                {
                                    "id": marathon_entity_id,
                                    "order": self.data[marathon_entity_id]["order"],
                                }
                            )

                    if 1 <= element.order <= len(marathon_entities):
                        changed_ids = []
                        change = 1

                        if dicted_element["order"] < self.data[element.id]["order"]:
                            changed_ids = [
                                entity["id"]
                                for entity in marathon_entities
                                if dicted_element["order"]
                                <= entity["order"]
                                < self.data[element.id]["order"]
                            ]
                        elif dicted_element["order"] > self.data[element.id]["order"]:
                            changed_ids = [
                                entity["id"]
                                for entity in marathon_entities
                                if self.data[element.id]["order"]
                                < entity["order"]
                                <= dicted_element["order"]
                            ]
                            change = -1

                        if changed_ids:
                            async with session.begin():
                                await session.execute(
                                    update(Marathons)
                                    .where(Marathons.id.in_(changed_ids))
                                    .values(order=Marathons.order + change)
                                )
                                for marathon_entity_id in changed_ids:
                                    self.data[marathon_entity_id]["order"] += change
                    else:
                        del dicted_element["order"]

                if dicted_element.get("steam_id"):
                    dicted_element.update(
                        await self.check_steam(dicted_element["steam_id"])
                    )

                async with session.begin():
                    await session.execute(
                        update(Marathons)
                        .where(Marathons.id == element.id)
                        .values(dicted_element)
                    )
                self.data[element.id].update(dicted_element)
                update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            self.resort()
            return update_info

    async def get_all(self, raw: bool) -> list[dict]:
        if raw:
            async with self.lock:
                result = []
                for item in self.data.values():
                    item_record = {}
                    for tag in (
                        "id",
                        "name",
                        "description",
                        "comment",
                        "status",
                        "date_start",
                        "date_end",
                        "picture",
                        "rules",
                        "records",
                        "order",
                        "link",
                        "marathon_id",
                        "steam_id",
                    ):
                        if item[tag]:
                            if tag == "picture" and not item[tag].startswith("/static"):
                                continue
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
        return self.sorted_list
