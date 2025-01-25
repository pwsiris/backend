import asyncio
from datetime import date as ddate
from datetime import datetime
from datetime import time as dtime

import httpx
from common.config import cfg
from common.errors import HTTPabort
from db.common import get_model_dict
from db.models import SCHEMA, Games
from fastapi.encoders import jsonable_encoder
from schemas import games as schema_games
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class GamesData:
    def __init__(self) -> None:
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
        cfg.logger.info("Games info was loaded to memory")

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
                games,
                key=lambda game: (
                    (game["subname"] or game["name"]).lower(),
                    game["name"].lower(),
                ),
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

                    if not dicted_element["link"]:
                        dicted_element["link"] = additional_info.get("link")
                    if not dicted_element["picture"]:
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

    async def get_all(self, raw: bool, types: list[str] = []) -> dict | list:
        if raw:
            async with self.lock:
                result = []
                for item in self.data.values():
                    item_record = {}
                    for tag in (
                        "id",
                        "name",
                        "subname",
                        "picture",
                        "status",
                        "genre",
                        "type",
                        "records",
                        "comment",
                        "gift_by",
                        "order_by",
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

    async def get_customers(self) -> list:
        async with self.lock:
            result = {
                "all": 0,
                "gifts": 0,
                "orders": 0,
                "gifts+orders": 0,
                "non-unique games": [],
                "people": {},
            }
            by_customers = {}
            for game in self.data.values():
                gift_by = (
                    [customer.strip() for customer in game["gift_by"].split("+")]
                    if game["gift_by"]
                    else []
                )
                order_by = (
                    [customer.strip() for customer in game["order_by"].split("+")]
                    if game["order_by"]
                    else []
                )
                customers = set(gift_by + order_by)
                if customers:
                    result["all"] += 1

                status = f"({game['status']})" if game["status"] else ""
                if len(customers) > 1:
                    result["non-unique games"].append(
                        f"{game['name']} {status}".strip()
                    )

                for customer in customers:
                    if customer not in by_customers:
                        by_customers[customer] = {
                            "gifts": {"list": [], "count": 0},
                            "orders": {"list": [], "count": 0},
                            "gifts+orders": {"list": [], "count": 0},
                            "count": 0,
                        }
                    if customer in gift_by and customer in order_by:
                        category = "gifts+orders"
                    elif customer in gift_by:
                        category = "gifts"
                    elif customer in order_by:
                        category = "orders"

                    by_customers[customer][category]["list"].append(
                        f"{game['name']} {status}".strip()
                    )
                    by_customers[customer][category]["count"] += 1
                    by_customers[customer]["count"] += 1

            result["all"] = f"{result['all']} / {len(self.data)}"
            result["non-unique games"] = sorted(
                result["non-unique games"], key=lambda game: game.lower()
            )

            for customer, info in by_customers.items():
                for category in ("gifts", "orders", "gifts+orders"):
                    by_customers[customer][category]["list"] = sorted(
                        info[category]["list"], key=lambda game: game.lower()
                    )
                    result[category] += by_customers[customer][category]["count"]
            result["people"] = by_customers

            return result

    async def update_pictures(
        self, session: AsyncSession, games_list: list[int]
    ) -> dict[int, str]:
        result = {}
        async with self.lock:
            for game_id in self.data:
                if games_list and game_id not in games_list:
                    result[game_id] = "Not found"
                    continue

                if game_id > self.non_steam_border or (
                    self.data[game_id]["picture"] or ""
                ).startswith("/static"):
                    continue

                new_steam_picture = (await self.check_steam(game_id)).get("picture")
                if not new_steam_picture:
                    result[game_id] = "No Steam picture"
                    continue

                if new_steam_picture != self.data[game_id]["picture"]:
                    async with session.begin():
                        await session.execute(
                            update(Games)
                            .where(Games.id == game_id)
                            .values(picture=new_steam_picture)
                        )
                        self.data[game_id]["picture"] = new_steam_picture
                        result[game_id] = "Updated"
                else:
                    if games_list:
                        result[game_id] = "Not updated"

        self.resort()
        return result
