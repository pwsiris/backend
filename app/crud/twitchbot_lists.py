import asyncio
import random
from datetime import datetime

from common.config import cfg
from common.errors import HTTPabort
from db.models import SCHEMA, TwitchBotLists
from schemas import twitchbot
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class TwitchBotList:
    def __init__(self, category: str) -> None:
        self.data = {}
        self.category = category
        self.lock = asyncio.Lock()

    async def setup(
        self,
        session: AsyncSession,
    ) -> None:
        async with session.begin():
            db_data = await session.scalars(
                select(TwitchBotLists).where(TwitchBotLists.category == self.category)
            )
            self.data = {element.id: element.value for element in db_data}

        cfg.logger.info(f"TwitchBot {self.category} info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    delete(TwitchBotLists).where(
                        TwitchBotLists.category == self.category
                    )
                )
            self.data = {}

    async def reset_all(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{TwitchBotLists.__table__.name} RESTART IDENTITY;"
                    )
                )

    async def add(
        self, session: AsyncSession, elements: list[twitchbot.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_elements_count = 0
            inserted_ids = []
            for element in elements:
                if element.value in list(self.data.values()):
                    inserted_ids.append(-1)
                    continue
                async with session.begin():
                    new_element = TwitchBotLists(
                        value=element.value, category=self.category
                    )
                    session.add(new_element)
                    await session.flush()
                    await session.refresh(new_element)
                    self.data[new_element.id] = new_element.value
                    inserted_ids.append(new_element.id)
                    inserted_elements_count += 1
            if not inserted_elements_count:
                HTTPabort(409, "Elements already exist")
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[twitchbot.DeletedElement]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            delete_info = []
            for element in elements:
                if element.id not in self.data:
                    delete_info.append("False")
                    continue
                async with session.begin():
                    await session.execute(
                        delete(TwitchBotLists).where(TwitchBotLists.id == element.id)
                    )
                del self.data[element.id]
                delete_info.append("True")
            if "True" not in delete_info:
                HTTPabort(404, "No elements to delete")
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[twitchbot.UpdatedElement]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            update_info = []
            for element in elements:
                if element.id not in self.data:
                    update_info.append("No element")
                    continue
                if element.value in list(self.data.values()):
                    update_info.append("New value not unique")
                    continue
                async with session.begin():
                    await session.execute(
                        update(TwitchBotLists)
                        .where(TwitchBotLists.id == element.id)
                        .values(value=element.value)
                    )
                self.data[element.id] = element.value
                update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            return update_info

    async def get_all(self, raw: bool) -> dict[int, str]:
        if raw:
            async with self.lock:
                result = []
                for id, value in self.data.items():
                    result.append({"id": id, "value": value})
                return sorted(result, key=lambda element: element["id"])
        return self.data

    def get_random(self) -> str:
        if self.data:
            random.seed(datetime.now().timestamp())
            return random.choice(list(self.data.values()))
        else:
            return ""

    def has(self, value: str) -> bool:
        return value in self.data.values()
