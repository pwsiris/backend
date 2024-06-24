import asyncio

import httpx
from common.config import cfg
from common.errors import HTTPabort
from common.utils import get_logger, levelDEBUG, levelINFO
from db.common import get_model_dict
from db.models import SCHEMA, Games
from schemas import games as schema_games
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class GamesData:
    def __init__(self) -> None:
        self.logger = get_logger(levelDEBUG if cfg.ENV == "dev" else levelINFO)
        self.data = {}
        self.lists = {}
        self.genres = {}
        self.lock = asyncio.Lock()

        self.non_steam_border = 1000 * 1000 * 1000 * 1000
        self.non_steam_game = 1000 * 1000 * 1000 * 1000

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Games))
            for row in db_data:
                if row.id > self.non_steam_border and row.id > self.non_steam_game:
                    self.non_steam_game = row.id
                self.data[row.id] = get_model_dict(row)
        self.resort()
        self.logger.info("Games info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Games.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.lists = {}
            self.genres = {}
            self.non_steam_game = self.non_steam_border

    def resort(self) -> None:
        typed_games = {}
        typed_genres = {}

        for game in self.data.values():
            game_type = game["type"] or "main"
            if game_type not in typed_games:
                typed_games[game_type] = []

            if game["records"]:
                game["records"] = sorted(
                    game["records"], key=lambda record: record.get("order", 1)
                )
            typed_games[game_type].append(game)

            if game_type not in typed_genres:
                typed_genres[game_type] = set()
            typed_genres[game_type].add(game["genre"])

        for game_type, games in typed_games.items():
            typed_games[game_type] = sorted(
                games, key=lambda game: (game["subname"] or game["name"], game["name"])
            )

        for game_type, genres in typed_genres.items():
            typed_genres[game_type] = sorted(genres)

        self.lists = typed_games
        self.genres = typed_genres

    async def check_steam(self, steam_id: int) -> dict:
        result = {}
        if steam_id < self.non_steam_border:
            result["link"] = f"https://store.steampowered.com/app/{steam_id}"
            try:
                templates = [
                    f"https://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/capsule_616x353.jpg",
                    f"https://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/header.jpg",
                    f"https://cdn.cloudflare.steamstatic.com/steam/apps/{steam_id}/header.jpg",
                ]
                for template in templates:
                    async with httpx.AsyncClient() as ac:
                        response = await ac.get(template)
                        if response.status_code == 200:
                            result["picture"] = template
                            break
                if not result.get("picture"):
                    self.logger.warning(f"No valid pic for steam-game {steam_id}")
            except Exception:
                self.logger.warning(f"Error getting steam-game {steam_id} pic")
        return result

    async def add(
        self, session: AsyncSession, elements: list[schema_games.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_elements_count = 0
            inserted_ids = []
            for element in elements:
                if element.id == None:
                    self.non_steam_game += 1
                    element.id = self.non_steam_game
                if element.id in self.data:
                    inserted_ids.append(-1)
                    continue

                additional_info = await self.check_steam(element.id)
                async with session.begin():
                    dicted_element = element.model_dump()
                    if dicted_element["link"] is None:
                        dicted_element["link"] = additional_info.get("link")
                    if dicted_element["picture"] is None:
                        dicted_element["picture"] = additional_info.get("picture")
                    new_game = Games(**dicted_element)
                    session.add(new_game)
                    self.data[element.id] = dicted_element

                    inserted_ids.append(element.id)
                    inserted_elements_count += 1
            if not inserted_elements_count:
                HTTPabort(409, "Elements already exist")
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_games.DeletedElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            delete_info = []
            for element in elements:
                if element.id not in self.data:
                    delete_info.append(False)
                    continue
                async with session.begin():
                    await session.execute(delete(Games).where(Games.id == element.id))
                del self.data[element.id]
                delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_games.UpdatedElement]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            update_info = []
            for element in elements:
                if element.id not in self.data:
                    update_info.append("No element")
                    continue
                if element.new_id in self.data:
                    update_info.append("Can't update id to existed game")
                    continue

                dicted_element = element.model_dump(
                    exclude={"id", "new_id"}, exclude_none=True
                )

                if element.new_id:
                    new_id = element.new_id
                    if element.new_id == -1:
                        self.non_steam_game += 1
                        new_id = self.non_steam_game
                    async with session.begin():
                        await session.execute(
                            update(Games)
                            .where(Games.id == element.id)
                            .values(id=new_id)
                        )
                    self.data[new_id] = self.data.pop(element.id)
                    element.id = new_id
                    dicted_element["id"] = new_id
                    dicted_element.update(await self.check_steam(element.id))

                for key, value in dicted_element.items():
                    if value in ("", []):
                        dicted_element[key] = None

                async with session.begin():
                    await session.execute(
                        update(Games)
                        .where(Games.id == element.id)
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

    async def get_genres(self, type: str) -> list[str]:
        return self.genres.get(type, [])

    async def update_genres(
        self, session: AsyncSession, elements: list[schema_games.UpdatedGenre]
    ) -> list[str]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            update_info = []
            for element in elements:
                if element.name not in self.genres:
                    update_info.append("No element")
                    continue
                if element.new_name in self.genres:
                    update_info.append("New name not unique")
                    continue

                async with session.begin():
                    await session.execute(
                        update(Games)
                        .where(Games.genre == element.name)
                        .values(genre=element.new_name)
                    )

                    for game_id, game_info in self.data.items():
                        if game_info["genre"] == element.name:
                            self.data[game_id]["genre"] == element.new_name
                update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            self.resort()
            return update_info
