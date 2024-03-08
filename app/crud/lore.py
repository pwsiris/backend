import asyncio

from common.errors import HTTPabort
from db.models import SCHEMA, Lore
from schemas import lore as schema_lore
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class LoreData:
    def __init__(self) -> None:
        self.data = {}
        self.texts = set()
        self.sorted_list = []
        self.lock = asyncio.Lock()

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Lore))
            for row in db_data:
                self.data[row.id] = {
                    "id": row.id,
                    "text": row.text,
                    "block_id": row.block_id,
                    "order": row.order,
                }
                self.texts.add(row.text)
        self.resort()
        print("INFO:\t  Lore info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Lore.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.texts = set()
            self.sorted_list = []

    def resort(self) -> None:
        self.sorted_list = sorted(
            list(self.data.values()), key=lambda lore: (lore["block_id"], lore["order"])
        )

    async def add(
        self, session: AsyncSession, elements: list[schema_lore.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_elements_count = 0
            inserted_ids = []
            for element in elements:
                if element.order and 1 <= element.order <= (len(self.data) + 1):
                    async with session.begin():
                        await session.execute(
                            update(Lore)
                            .where(Lore.order >= element.order)
                            .values(order=Lore.order + 1)
                        )
                        for social_id in self.data:
                            if self.data[social_id]["order"] >= element.order:
                                self.data[social_id]["order"] += 1
                else:
                    element.order = len(self.data) + 1

                async with session.begin():
                    new_lore = {
                        "text": element.text,
                        "block_id": element.block_id,
                        "order": element.order,
                    }
                    new_element = Lore(**new_lore)
                    session.add(new_element)
                    await session.flush()
                    await session.refresh(new_element)

                    new_lore["id"] = new_element.id
                    self.data[new_element.id] = new_lore
                    self.texts.add(element.text)

                    inserted_ids.append(new_element.id)
                    inserted_elements_count += 1
            if not inserted_elements_count:
                HTTPabort(409, "Elements already exist")
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_lore.DeletedElement]
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
                    await session.execute(delete(Lore).where(Lore.id == element.id))
                    await session.execute(
                        update(Lore)
                        .where(Lore.order > self.data[element.id]["order"])
                        .values(order=Lore.order - 1)
                    )
                    for lore_id in self.data:
                        if self.data[lore_id]["order"] > self.data[element.id]["order"]:
                            self.data[lore_id]["order"] -= 1
                    self.texts.remove(self.data[element.id]["text"])
                    del self.data[element.id]
                    delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_lore.UpdatedElement]
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
                if dicted_element.get("order") != None:
                    if 1 <= element.order <= len(self.data):
                        changed_orders = []
                        change = 1

                        if dicted_element["order"] < self.data[element.id]["order"]:
                            changed_orders = list(
                                range(
                                    dicted_element["order"],
                                    self.data[element.id]["order"],
                                )
                            )
                        elif dicted_element["order"] > self.data[element.id]["order"]:
                            changed_orders = list(
                                range(
                                    self.data[element.id]["order"] + 1,
                                    dicted_element["order"] + 1,
                                )
                            )
                            change = -1

                        if changed_orders:
                            async with session.begin():
                                await session.execute(
                                    update(Lore)
                                    .where(Lore.order.in_(changed_orders))
                                    .values(order=Lore.order + change)
                                )
                                for lore_id in self.data:
                                    if self.data[lore_id]["order"] in changed_orders:
                                        self.data[lore_id]["order"] += change
                    else:
                        del dicted_element["order"]

                async with session.begin():
                    await session.execute(
                        update(Lore).where(Lore.id == element.id).values(dicted_element)
                    )
                self.data[element.id].update(dicted_element)
                update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            self.resort()
            return update_info

    async def get_all(self) -> list[dict]:
        return self.sorted_list
