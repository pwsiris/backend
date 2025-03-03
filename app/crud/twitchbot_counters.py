import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from common.config import cfg
from db.models import SCHEMA, TwitchBotCounters
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class TwitchBotCounter:
    def __init__(self, counter_type: str) -> None:
        self.data = {}
        self.type = counter_type
        self.lock = asyncio.Lock()

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(
                select(TwitchBotCounters).where(TwitchBotCounters.type == self.type)
            )
            self.data = {
                element.name: {"count": element.value, "updated": element.updated}
                for element in db_data
            }

        cfg.logger.info(f"TwitchBot {self.type} counter info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    delete(TwitchBotCounters).where(TwitchBotCounters.type == self.type)
                )
            self.data = {}

    async def reset_all(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{TwitchBotCounters.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}

    async def set(self, session: AsyncSession, name: str, value: int) -> str:
        async with self.lock:
            async with session.begin():
                if name not in self.data:
                    if value > -1:
                        session.add(
                            TwitchBotCounters(name=name, type=self.type, value=value)
                        )
                        self.data[name] = {"count": value, "updated": None}
                        return str(value)
                    else:
                        return "не добавлено"
                else:
                    if value > -1:
                        await session.execute(
                            update(TwitchBotCounters)
                            .where(
                                TwitchBotCounters.name == name,
                                TwitchBotCounters.type == self.type,
                            )
                            .values(value=value)
                        )
                        self.data[name]["count"] = value
                        return str(value)
                    else:
                        await session.execute(
                            delete(TwitchBotCounters).where(
                                TwitchBotCounters.name == name,
                                TwitchBotCounters.type == self.type,
                            )
                        )
                        del self.data[name]
                        return "удалено"

    async def get_value(self, name: str, default: Any) -> int | None:
        async with self.lock:
            return self.data.get(name, {}).get("count", default)

    async def get_all(self, raw: bool = False) -> str:
        async with self.lock:
            return ", ".join(name.upper() for name in self.data.keys())

    async def update(
        self, session: AsyncSession, name: str, with_delay: bool, increment: int = 1
    ) -> str:
        async with self.lock:
            if name not in self.data:
                return "Нет счётчика"

            now = datetime.now(timezone.utc)
            updated = self.data[name]["updated"] or datetime.fromisoformat(
                "1970-01-01T00:00:00+00:00"
            )
            if with_delay and (now - updated < timedelta(seconds=30)):
                return "Cлишком быстрое изменение счётчика"

            async with session.begin():
                await session.execute(
                    update(TwitchBotCounters)
                    .where(
                        TwitchBotCounters.name == name,
                        TwitchBotCounters.type == self.type,
                    )
                    .values(value=(self.data[name]["count"] + increment), updated=now)
                )
                self.data[name]["count"] += increment
                self.data[name]["updated"] = now
            return str(self.data[name]["count"])
