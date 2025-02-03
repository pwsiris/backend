import asyncio
from copy import deepcopy
from datetime import date as ddate
from datetime import datetime
from datetime import time as dtime

from common.config import cfg
from common.errors import HTTPabort
from db.common import get_model_dict
from db.models import SCHEMA, Auctions
from fastapi.encoders import jsonable_encoder
from schemas import auctions as schema_auctions
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class AuctionsData:
    def __init__(self) -> None:
        self.data = {}
        self.sorted_list = []
        self.lock = asyncio.Lock()

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Auctions))
            for row in db_data:
                self.data[row.id] = get_model_dict(row)
        self.resort()
        cfg.logger.info("Auctions info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Auctions.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.sorted_list = []

    def resort(self) -> None:
        auctions_entities = sorted(
            self.data.values(), key=lambda auction_entity: auction_entity["order"] or 0
        )
        auctions = {}
        for auction_entity in auctions_entities:
            auction_entity_copy = deepcopy(auction_entity)
            if auction_entity_copy["date"]:
                auction_entity_copy["date"] = auction_entity_copy["date"].isoformat()

            id = auction_entity["id"]
            a_id = auction_entity["auction_id"]

            if a_id:
                if a_id not in auctions:
                    auctions[a_id] = {"list": [], "participants": []}

                if auction_entity["order"]:
                    auctions[a_id]["list"].append(auction_entity_copy)
                else:
                    auctions[a_id]["participants"].append(auction_entity_copy)
            else:
                if id in auctions:
                    auctions[id].update(auction_entity_copy)
                else:
                    auction = auction_entity_copy
                    auction["list"] = []
                    auction["participants"] = []
                    auctions[id] = auction

        for auction_id in auctions:
            try:
                if auctions[auction_id]["list"][-1]["status"] in (
                    "Просмотрено",
                    "Пройдено",
                    "Заброшено",
                ):
                    auctions[auction_id]["status"] = "Завершено"
                elif auctions[auction_id]["list"][0]["status"] != None:
                    auctions[auction_id]["status"] = "В процессе"
            except Exception:
                pass

        self.sorted_list = sorted(
            auctions.values(), key=lambda auction: auction["order"]
        )

    async def add(
        self, session: AsyncSession, elements: list[schema_auctions.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_ids = []
            for element in elements:
                if element.auction_id:
                    if element.auction_id not in self.data:
                        inserted_ids.append(-1)
                        continue
                if element.order:
                    auction_entities = []
                    for auction_entity_id in self.data:
                        if (
                            self.data[auction_entity_id]["auction_id"]
                            == element.auction_id
                        ):
                            auction_entities.append(
                                {
                                    "id": auction_entity_id,
                                    "order": self.data[auction_entity_id]["order"],
                                }
                            )
                    if 1 <= element.order <= len(auction_entities):
                        async with session.begin():
                            await session.execute(
                                update(Auctions)
                                .where(
                                    Auctions.auction_id == element.auction_id,
                                    Auctions.order >= element.order,
                                )
                                .values(order=Auctions.order + 1)
                            )
                            for auction_entity_id in self.data:
                                if (
                                    self.data[auction_entity_id]["auction_id"]
                                    == element.auction_id
                                    and self.data[auction_entity_id]["order"]
                                    >= element.order
                                ):
                                    self.data[auction_entity_id]["order"] += 1
                    else:
                        element.order = len(auction_entities) + 1

                async with session.begin():
                    dicted_element = element.model_dump()

                    new_auction_entity = Auctions(**dicted_element)
                    session.add(new_auction_entity)
                    await session.flush()
                    await session.refresh(new_auction_entity)

                    dicted_element["id"] = new_auction_entity.id
                    self.data[new_auction_entity.id] = dicted_element

                    inserted_ids.append(new_auction_entity.id)
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_auctions.DeletedElement]
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
                        delete(Auctions).where(Auctions.id == element.id)
                    )
                    await session.execute(
                        delete(Auctions).where(Auctions.auction_id == element.id)
                    )
                    await session.execute(
                        update(Auctions)
                        .where(
                            Auctions.auction_id == self.data[element.id]["auction_id"],
                            Auctions.order > self.data[element.id]["order"],
                        )
                        .values(order=Auctions.order - 1)
                    )
                    for auction_entity_id in self.data:
                        if (
                            self.data[auction_entity_id]["auction_id"]
                            == self.data[element.id]["auction_id"]
                            and self.data[auction_entity_id]["order"]
                            > self.data[element.id]["order"]
                        ):
                            self.data[auction_entity_id]["order"] -= 1
                    del self.data[element.id]
                    delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_auctions.UpdatedElement]
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

                new_auction_id = dicted_element.get("auction_id")
                if new_auction_id != None:
                    await session.execute(
                        update(Auctions)
                        .where(
                            Auctions.auction_id == self.data[element.id]["auction_id"],
                            Auctions.order > self.data[element.id]["order"],
                        )
                        .values(order=Auctions.order - 1)
                    )
                    new_element_position = 1
                    for auction_entity_id in self.data:
                        if (
                            self.data[auction_entity_id]["auction_id"]
                            == self.data[element.id]["auction_id"]
                            and self.data[auction_entity_id]["order"]
                            > self.data[element.id]["order"]
                        ):
                            self.data[auction_entity_id]["order"] -= 1
                        if self.data[auction_entity_id] == new_auction_id:
                            new_element_position += 1

                    await session.execute(
                        update(Auctions)
                        .where(Auctions.id == element.id)
                        .values(order=new_element_position)
                    )
                    self.data[element.id]["order"] = new_element_position

                if dicted_element.get("order") != None:
                    auction_entities = []
                    for auction_entity_id in self.data:
                        if (
                            self.data[auction_entity_id]["auction_id"]
                            == self.data[element.id]["auction_id"]
                        ):
                            auction_entities.append(
                                {
                                    "id": auction_entity_id,
                                    "order": self.data[auction_entity_id]["order"],
                                }
                            )

                    if 1 <= element.order <= len(auction_entities):
                        changed_ids = []
                        change = 1

                        if dicted_element["order"] < self.data[element.id]["order"]:
                            changed_ids = [
                                entity["id"]
                                for entity in auction_entities
                                if dicted_element["order"]
                                <= entity["order"]
                                < self.data[element.id]["order"]
                            ]
                        elif dicted_element["order"] > self.data[element.id]["order"]:
                            changed_ids = [
                                entity["id"]
                                for entity in auction_entities
                                if self.data[element.id]["order"]
                                < entity["order"]
                                <= dicted_element["order"]
                            ]
                            change = -1

                        if changed_ids:
                            async with session.begin():
                                await session.execute(
                                    update(Auctions)
                                    .where(Auctions.id.in_(changed_ids))
                                    .values(order=Auctions.order + change)
                                )
                                for auction_entity_id in changed_ids:
                                    self.data[auction_entity_id]["order"] += change
                    else:
                        del dicted_element["order"]

                async with session.begin():
                    await session.execute(
                        update(Auctions)
                        .where(Auctions.id == element.id)
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
                        "date",
                        "description",
                        "comment",
                        "status",
                        "picture",
                        "order",
                        "order_by",
                        "auction_id",
                    ):
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
