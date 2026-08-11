import asyncio
from datetime import date as ddate
from datetime import datetime
from datetime import time as dtime

from common.config import cfg
from common.errors import HTTPabort
from db.common import get_model_dict
from db.models import SCHEMA, Cinema
from fastapi.encoders import jsonable_encoder
from schemas import cinema as schema_cinema
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

UNIX_BELOW_ZERO_DATE = ddate.fromisoformat("1969-12-31")


class CinemaData:
    def __init__(self) -> None:
        self.data = {}
        self.lists = {}
        self.lock = asyncio.Lock()
        self.default_types_order = ["Фильмы", "Мультфильмы", "Сериалы"]
        self.types = []
        self.status_mapping = {
            "Смотрим": 1,
            "Смотрю": 1,
            "": 2,
            "Просмотрено": 3,
            "Отложено": 4,
            "Заброшено": 5,
        }

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Cinema))
            for row in db_data:
                self.data[row.id] = get_model_dict(row)
        self.default_types_order = ["Фильмы", "Мультфильмы", "Сериалы"]
        self.resort()
        cfg.logger.info("Cinema info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Cinema.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.lists = {}

    def resort(self) -> None:
        typed_cinema = {}

        for cinema in self.data.values():
            cinema_type = cinema["type"]
            if cinema_type not in typed_cinema:
                typed_cinema[cinema_type] = []
            typed_cinema[cinema_type].append(cinema)

        for cinema_type, cinemas in typed_cinema.items():
            typed_cinema[cinema_type] = sorted(
                cinemas,
                key=lambda cinema: (
                    self.status_mapping.get(cinema["status"] or "", 6),
                    (cinema["subname"] or cinema["name"]).lower(),
                    cinema["name"].lower(),
                ),
            )

        self.lists = jsonable_encoder(
            typed_cinema,
            custom_encoder={
                ddate: lambda date_obj: (date_obj.isoformat()),
            },
        )

        self.types = [t for t in self.default_types_order if t in self.lists]
        self.types.extend(
            sorted([t for t in self.lists.keys() if t not in self.default_types_order])
        )

    async def add(
        self, session: AsyncSession, elements: list[schema_cinema.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_ids = []
            for element in elements:
                async with session.begin():
                    dicted_element = element.model_dump()

                    new_cinema = Cinema(**dicted_element)
                    session.add(new_cinema)
                    await session.flush()
                    await session.refresh(new_cinema)

                    dicted_element["id"] = new_cinema.id
                    self.data[new_cinema.id] = dicted_element

                    inserted_ids.append(new_cinema.id)
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_cinema.DeletedElement]
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
                    await session.execute(delete(Cinema).where(Cinema.id == element.id))
                del self.data[element.id]
                delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_cinema.UpdatedElement]
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

                for key, value in dicted_element.items():
                    if value in ("", UNIX_BELOW_ZERO_DATE):
                        dicted_element[key] = None

                async with session.begin():
                    await session.execute(
                        update(Cinema)
                        .where(Cinema.id == element.id)
                        .values(dicted_element)
                    )
                self.data[element.id].update(dicted_element)
                update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            self.resort()
            return update_info

    async def get_all(self, raw: bool, types: list[str] = []) -> dict[list[dict]]:
        if raw:
            async with self.lock:
                result = []
                for item in self.data.values():
                    item_record = {}
                    for tag in (
                        "id",
                        "name",
                        "subname",
                        "type",
                        "event",
                        "comment",
                        "date",
                        "status",
                        "order_by",
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

        if types:
            result = {}
            for type in types:
                result[type] = self.lists.get(type, [])
            return result
        return self.lists

    async def get_types(self) -> list[str]:
        return self.types

    async def set_default_types_order(self, input_types: list[str]) -> None:
        async with self.lock:
            self.default_types_order = input_types
            self.resort()

    async def get_customers(self) -> list:
        async with self.lock:
            result = {"all": len(self.data), "orders": 0, "people": {}}
            by_customers = {}
            for cinema in self.data.values():
                customers = (cinema["order_by"] or "").split("+")
                if customers:
                    for customer in customers:
                        if customer not in by_customers:
                            by_customers[customer] = {
                                "list": [],
                                "count": 0,
                            }

                        status = f"({cinema['status']})" if cinema["status"] else ""
                        date = (
                            f"({cinema['date'].isoformat()})" if cinema["date"] else ""
                        )
                        by_customers[customer]["list"].append(
                            (f"{cinema['name']} {status} {date}").strip()
                        )
                        by_customers[customer]["count"] += 1
                    if customers != [""]:
                        result["orders"] += 1
            for customer, info in by_customers.items():
                by_customers[customer]["list"] = sorted(
                    info["list"], key=lambda cinema: cinema.lower()
                )
            result["people"] = by_customers
            return result
