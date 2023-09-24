import asyncio
import random
from datetime import datetime

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

        print(f"INFO:\t  TwitchBot {self.category} info was loaded to memory")

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
                if element.value in self.data.values():
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
    ) -> None:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            deleted_elements_count = 0
            for element in elements:
                if element.id not in self.data:
                    continue
                async with session.begin():
                    await session.execute(
                        delete(TwitchBotLists).where(TwitchBotLists.id == element.id)
                    )
                del self.data[element.id]
                deleted_elements_count += 1
            if not deleted_elements_count:
                HTTPabort(404, "No elements to delete")

    async def update(
        self, session: AsyncSession, elements: list[twitchbot.UpdatedElement]
    ) -> None:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            updated_elements_count = 0
            for element in elements:
                if element.id not in self.data:
                    continue
                async with session.begin():
                    await session.execute(
                        update(TwitchBotLists)
                        .where(TwitchBotLists.id == element.id)
                        .values(value=element.value)
                    )
                self.data[element.id] = element.value
                updated_elements_count += 1
            if not updated_elements_count:
                HTTPabort(404, "No elements to update")

    async def get_all(self) -> dict[int, str]:
        async with self.lock:
            return self.data

    def get_random(self) -> str:
        if self.data:
            random.seed(datetime.now().timestamp())
            return random.choice(list(self.data.values()))
        else:
            return ""

    def has(self, value: str) -> bool:
        return value in self.data.values()
