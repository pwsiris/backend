import asyncio

from common.errors import HTTPabort
from db.models import SCHEMA, Merch
from schemas import merch as schema_merch
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class MerchData:
    def __init__(self) -> None:
        self.data = {}
        self.sorted_list = []
        self.lock = asyncio.Lock()

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Merch))
            for row in db_data:
                self.data[row.id] = {
                    "id": row.id,
                    "name": row.name,
                    "description": row.description,
                    "price": row.price,
                    "status": row.status,
                    "creator_name": row.creator_name,
                    "creator_link": row.creator_link,
                    "picture": row.picture,
                    "picture_size": row.picture_size,
                    "order": row.order,
                }
        self.resort()
        print("INFO:\t  Merch info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Merch.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.sorted_list = []

    def resort(self) -> None:
        self.sorted_list = sorted(
            list(self.data.values()), key=lambda merch: merch["order"]
        )

    async def add(
        self, session: AsyncSession, elements: list[schema_merch.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            new_elements = []
            for element in elements:
                if (
                    not element.order
                    or element.order <= 0
                    or element.order > len(self.data)
                ):
                    element.order = len(self.data) + len(new_elements) + 1
                new_elements.append(element.model_dump())

            sorted_new_elements = sorted(
                new_elements, key=lambda element: element["order"]
            )
            new_orders = {id: merch["order"] for id, merch in self.data.items()}

            for element in sorted_new_elements:
                for id in new_orders:
                    if new_orders[id] >= element["order"]:
                        new_orders[id] += 1

            new_orders_minimized = {}
            for id in new_orders:
                if new_orders[id] != self.data[id]["order"]:
                    new_orders_minimized[id] = new_orders[id]

            new_ids = []
            async with session.begin():
                ids = await session.execute(
                    insert(Merch).values(new_elements).returning(Merch.id)
                )
                new_ids = [id for id, in ids]

                if len(new_ids) != len(new_elements) or not all(
                    isinstance(id, int) for id in new_ids
                ):
                    await session.rollback()
                    HTTPabort(400, "Inserting new elements error")

                if new_orders_minimized:
                    await session.execute(
                        update(Merch),
                        [
                            {"id": id, "order": order}
                            for id, order in new_orders_minimized.items()
                        ],
                    )

                for id, element in zip(new_ids, new_elements):
                    self.data[id] = {**element, "id": id}

                for id, order in new_orders_minimized.items():
                    self.data[id]["order"] = order
            self.resort()
            return new_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_merch.DeletedElement]
    ) -> list[bool]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            delete_info = []
            ids_for_delete = []
            for element in elements:
                if element.id not in self.data:
                    delete_info.append(False)
                    continue
                delete_info.append(True)
                ids_for_delete.append(element.id)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")

            orders = [
                {"id": id, "order": self.data[id]["order"]}
                for id in self.data
                if id not in ids_for_delete
            ]
            orders.sort(key=lambda element: element["order"])

            orders_minimized = []
            for idx in range(len(orders)):
                if idx + 1 != orders[idx]["order"]:
                    orders_minimized.append({"id": orders[idx]["id"], "order": idx + 1})

            async with session.begin():
                await session.execute(delete(Merch).where(Merch.id.in_(ids_for_delete)))

                if orders_minimized:
                    await session.execute(update(Merch), orders_minimized)

                for id in ids_for_delete:
                    del self.data[id]

                for order in orders_minimized:
                    self.data[order["id"]]["order"] = order["order"]

            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_merch.UpdatedElement]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            update_info = []
            ids_for_order_update = []
            updated_orders = []
            updated_elements = []
            for element in elements:
                if element.id not in self.data:
                    update_info.append("No element")
                    continue
                update_info.append("Updated")
                updated_elements.append(element.model_dump(exclude_none=True))
                if element.order and (1 <= element.order <= len(self.data)):
                    ids_for_order_update.append(element.id)
                    updated_orders.append({"id": element.id, "order": element.order})
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")

            new_orders_minimized = {}
            if ids_for_order_update:
                orders = [
                    {"id": id, "order": self.data[id]["order"]}
                    for id in self.data
                    if id not in ids_for_order_update
                ]
                orders.sort(key=lambda element: element["order"])
                for idx in range(len(orders)):
                    orders[idx]["order"] = idx + 1
                new_orders = {element["id"]: element["order"] for element in orders}

                updated_orders.sort(key=lambda element: element["order"])
                for element in updated_orders:
                    for id in new_orders:
                        if new_orders[id] >= element["order"]:
                            new_orders[id] += 1

                for id in new_orders:
                    if new_orders[id] != self.data[id]["order"]:
                        new_orders_minimized[id] = new_orders[id]

            async with session.begin():
                await session.execute(update(Merch), updated_elements)

                if new_orders_minimized:
                    await session.execute(
                        update(Merch),
                        [
                            {"id": id, "order": order}
                            for id, order in new_orders_minimized.items()
                        ],
                    )

                for element in updated_elements:
                    self.data[element["id"]].update(element)

                for id, order in new_orders_minimized.items():
                    self.data[id]["order"] = order
            self.resort()
            return update_info

    async def get_all(self) -> list[dict]:
        return self.sorted_list
