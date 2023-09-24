import asyncio

from common.errors import HTTPabort
from db.models import SCHEMA, Challenges
from schemas import challenges as schema_challenges
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class ChallengesData:
    def __init__(self) -> None:
        self.data = {}
        self.lists = {}
        self.lock = asyncio.Lock()
        self.status_mapping = {
            "В процессе": 1,
            "": 2,
            "Сделано": 3,
            "Дропнуто": 4,
        }

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Challenges))
            for row in db_data:
                self.data[row.id] = {
                    "id": row.id,
                    "name": row.name,
                    "picture": row.picture,
                    "order_by": row.order_by,
                    "description": row.description,
                    "comment": row.comment,
                    "status": row.status,
                    "type": row.type,
                    "price": row.price,
                    "records": row.records,
                }
        self.resort()
        print("INFO:\t  Challenges info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Challenges.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.lists = {}

    def resort(self) -> None:
        typed_challenges = {}
        for challenge in self.data.values():
            challenge_type = challenge["type"] or "main"
            if challenge_type not in typed_challenges:
                typed_challenges[challenge_type] = []
            typed_challenges[challenge_type].append(challenge)

        for challenge_type, challenges in typed_challenges.items():
            typed_challenges[challenge_type] = sorted(
                challenges,
                key=lambda challenge: (
                    self.status_mapping.get(challenge["status"] or "", 4),
                    challenge["name"],
                ),
            )

        self.lists = typed_challenges

    async def add(
        self, session: AsyncSession, elements: list[schema_challenges.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_elements_count = 0
            inserted_ids = []
            for element in elements:
                async with session.begin():
                    new_challenge = {
                        "name": element.name,
                        "picture": element.picture,
                        "order_by": element.order_by,
                        "description": element.description,
                        "comment": element.comment,
                        "status": element.status,
                        "type": element.type,
                        "price": element.price,
                        "records": element.records,
                    }
                    new_element = Challenges(**new_challenge)
                    session.add(new_element)
                    await session.flush()
                    await session.refresh(new_element)
                    new_challenge["id"] = new_element.id
                    self.data[new_element.id] = new_challenge
                    inserted_ids.append(new_element.id)
                    inserted_elements_count += 1
            if not inserted_elements_count:
                HTTPabort(409, "Elements already exist")
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_challenges.DeletedElement]
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
                        delete(Challenges).where(Challenges.id == element.id)
                    )
                    del self.data[element.id]
                    delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_challenges.UpdatedElement]
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
                    if value == "":
                        dicted_element[key] = None

                async with session.begin():
                    await session.execute(
                        update(Challenges)
                        .where(Challenges.id == element.id)
                        .values(dicted_element)
                    )
                    self.data[element.id].update(dicted_element)
                    update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            self.resort()
            return update_info

    async def get_all(self, types: list[str]) -> dict:
        if types:
            result = {}
            for type in types:
                result[type] = self.lists.get(type, [])
            return result
        return self.lists
