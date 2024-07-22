import asyncio
from datetime import datetime, timezone

import httpx
from common.config import cfg
from common.errors import HTTPabort
from common.utils import get_logger, levelDEBUG, levelINFO
from db.common import get_model_dict
from db.models import SCHEMA, Anime
from fastapi.encoders import jsonable_encoder
from schemas import anime as schema_anime
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

UNIX_ZERO = datetime.fromisoformat("1970-01-01 00:00+00:00")
UNIX_BELOW_ZERO = datetime.fromisoformat("1969-12-31 23:59:59+00:00")


class AnimeData:
    def __init__(self) -> None:
        self.logger = get_logger(levelDEBUG if cfg.ENV == "dev" else levelINFO)
        self.data = {}
        self.sorted_list = []
        self.lock = asyncio.Lock()
        self.status_mapping = {
            "Смотрим": 1,
            "": 2,
            "Просмотрено": 3,
            "Заброшено": 3,
        }
        self.type_mapping = {
            "tv": "Сериал",
            "movie": "Фильм",
            "ova": "OVA",
            "special": "Спецвыпуск",
        }
        self.non_mal_border = 1000 * 1000 * 1000 * 1000
        self.non_mal_anime = 1000 * 1000 * 1000 * 1000

    async def setup(self, session: AsyncSession) -> None:
        async with session.begin():
            db_data = await session.scalars(select(Anime))
            for row in db_data:
                if row.id > self.non_mal_border and row.id > self.non_mal_anime:
                    self.non_mal_anime = row.id
                self.data[row.id] = get_model_dict(row)
        self.resort()
        self.logger.info("Anime info was loaded to memory")

    async def reset(self, session: AsyncSession) -> None:
        async with self.lock:
            async with session.begin():
                await session.execute(
                    text(
                        f"TRUNCATE TABLE {SCHEMA}.{Anime.__table__.name} RESTART IDENTITY;"
                    )
                )
            self.data = {}
            self.sorted_list = []
            self.non_mal_anime = self.non_mal_border

    async def get_anime_mal_info(self, id: int) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=cfg.MAL_API,
                params={"fields": "mean,media_type,status,num_episodes"},
                headers={cfg.MAL_HEADER: cfg.MAL_CLIENT_ID},
            ) as ac:
                response = await ac.get(f"/anime/{id}")
                if response.status_code != 200:
                    details = ""
                    try:
                        details = str(response.json())
                    except Exception:
                        pass
                    self.logger.warning(
                        f"Error getting anime {id} info. Code: {response.status_code}, Details: {details}."
                    )
                    return {}
        except Exception:
            self.logger.warning(f"Error getting anime {id} info from MAL api")
            return {}

        try:
            anime_info = response.json()
            return {
                "link": f"https://myanimelist.net/anime/{id}",
                "picture": anime_info["main_picture"]["large"],
                "type": self.type_mapping.get(
                    anime_info["media_type"].lower(), anime_info["media_type"]
                ),
                "episodes": anime_info["num_episodes"],
            }
        except Exception:
            self.logger.warning(f"Error getting anime {id} details from API response")
            return {}

    def resort(self) -> None:
        seriesed = {}
        for anime in self.data.values():
            if anime["series"]:
                if anime["series"] not in seriesed:
                    seriesed[anime["series"]] = {
                        "name": anime["series"],
                        "status": anime["status"],
                        "added_time": anime["added_time"],
                        "completed_time": anime["completed_time"],
                        "list": [anime],
                    }
                    if anime["score"]:
                        seriesed[anime["series"]]["score_sum"] = anime["score"]
                        seriesed[anime["series"]]["score_count"] = 1
                    continue

                curr_series = seriesed[anime["series"]]
                updated_data = {}

                if curr_series["status"] != anime["status"]:
                    updated_data["status"] = "Смотрим"
                    updated_data["completed_time"] = None

                if (
                    curr_series["status"] == "Заброшено"
                    or anime["status"] == "Заброшено"
                ):
                    updated_data["status"] = "Заброшено"
                    if (anime["completed_time"] or UNIX_ZERO) > (
                        curr_series["completed_time"] or UNIX_ZERO
                    ):
                        updated_data["completed_time"] = anime["completed_time"]
                    else:
                        updated_data["completed_time"] = curr_series["completed_time"]

                if curr_series["status"] == anime["status"] == "Просмотрено":
                    if anime["completed_time"] > curr_series["completed_time"]:
                        updated_data["completed_time"] = anime["completed_time"]

                if (anime["added_time"] or UNIX_ZERO) < (
                    curr_series["added_time"] or UNIX_ZERO
                ):
                    updated_data["added_time"] = anime["added_time"]

                if anime["score"]:
                    if seriesed[anime["series"]].get("score_sum", None) != None:
                        seriesed[anime["series"]]["score_sum"] += anime["score"]
                        seriesed[anime["series"]]["score_count"] += 1
                    else:
                        seriesed[anime["series"]]["score_sum"] = anime["score"]
                        seriesed[anime["series"]]["score_count"] = 1

                seriesed[anime["series"]].update(updated_data)
                seriesed[anime["series"]]["list"].append(anime)

        for anime_series in seriesed:
            if seriesed[anime_series].get("score_sum", None) != None:
                if seriesed[anime_series]["status"] != "Заброшено":
                    seriesed[anime_series]["score"] = round(
                        seriesed[anime_series]["score_sum"]
                        / seriesed[anime_series]["score_count"],
                        1,
                    )
                del seriesed[anime_series]["score_sum"]
                del seriesed[anime_series]["score_count"]

        all_anime = [anime for anime in self.data.values() if not anime["series"]]

        for series in seriesed.values():
            series["list"] = sorted(
                series["list"],
                key=lambda anime: (
                    self.status_mapping.get(anime["status"] or "", 4),
                    int(
                        (
                            anime["completed_time"] or anime["added_time"] or UNIX_ZERO
                        ).timestamp()
                    ),
                ),
            )
            all_anime.append(series)

        self.sorted_list = jsonable_encoder(
            sorted(
                all_anime,
                key=lambda anime: (
                    self.status_mapping.get(anime["status"] or "", 4),
                    -int((anime["completed_time"] or UNIX_ZERO).timestamp())
                    or int((anime["added_time"] or UNIX_ZERO).timestamp()),
                ),
            ),
            custom_encoder={
                datetime: lambda datetime_obj: (datetime_obj.isoformat()).replace(
                    "T", " "
                )
            },
        )

    async def add(
        self, session: AsyncSession, elements: list[schema_anime.NewElement]
    ) -> list[int]:
        if not elements:
            return HTTPabort(422, "Empty list")
        async with self.lock:
            inserted_elements_count = 0
            inserted_ids = []
            for element in elements:
                if element.id == None:
                    self.non_mal_anime += 1
                    element.id = self.non_mal_anime
                if element.id in self.data:
                    inserted_ids.append(-1)
                    continue
                additional_info = await self.get_anime_mal_info(element.id)
                async with session.begin():
                    dicted_element = element.model_dump()

                    for key in ("link", "type", "episodes", "picture"):
                        if dicted_element[key] is None:
                            dicted_element[key] = additional_info.get(key)

                    dicted_element["added_time"] = (
                        (dicted_element["added_time"] or datetime.now(timezone.utc))
                        if dicted_element["added_time"] != UNIX_BELOW_ZERO
                        else None
                    )
                    dicted_element["completed_time"] = (
                        (dicted_element["completed_time"] or datetime.now(timezone.utc))
                        if dicted_element["status"] in ("Просмотрено", "Заброшено")
                        else None
                    )

                    new_anime = Anime(**dicted_element)
                    session.add(new_anime)
                    self.data[element.id] = dicted_element

                    inserted_ids.append(element.id)
                    inserted_elements_count += 1
            if not inserted_elements_count:
                HTTPabort(409, "Elements already exist")
            self.resort()
            return inserted_ids

    async def delete(
        self, session: AsyncSession, elements: list[schema_anime.DeletedElement]
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
                    await session.execute(delete(Anime).where(Anime.id == element.id))
                del self.data[element.id]
                delete_info.append(True)
            if True not in delete_info:
                HTTPabort(404, "No elements to delete")
            self.resort()
            return delete_info

    async def update(
        self, session: AsyncSession, elements: list[schema_anime.UpdatedElement]
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
                    update_info.append("Can't update id to existed anime")
                    continue

                dicted_element = element.model_dump(
                    exclude={"id", "new_id"}, exclude_none=True
                )

                if element.new_id:
                    new_id = element.new_id
                    if element.new_id == -1:
                        self.non_mal_anime += 1
                        new_id = self.non_mal_anime
                    async with session.begin():
                        await session.execute(
                            update(Anime)
                            .where(Anime.id == element.id)
                            .values(id=new_id)
                        )
                    self.data[new_id] = self.data.pop(element.id)
                    element.id = new_id
                    dicted_element["id"] = new_id
                    dicted_element.update(await self.get_anime_mal_info(element.id))

                if dicted_element.get("status") in ("Просмотрено", "Заброшено"):
                    dicted_element["completed_time"] = dicted_element.get(
                        "completed_time"
                    ) or datetime.now(timezone.utc)
                elif dicted_element.get("status") in ("", "Смотрим"):
                    dicted_element["completed_time"] = None

                # erasing non-string fields
                if dicted_element.get("episodes") == -1:
                    dicted_element["episodes"] = None
                if dicted_element.get("score") == -1:
                    dicted_element["score"] = None
                if dicted_element.get("completed_time") == UNIX_BELOW_ZERO:
                    dicted_element["completed_time"] = None
                if dicted_element.get("added_time") == UNIX_BELOW_ZERO:
                    dicted_element["added_time"] = None

                for key, value in dicted_element.items():
                    if value == "":
                        dicted_element[key] = None
                async with session.begin():
                    await session.execute(
                        update(Anime)
                        .where(Anime.id == element.id)
                        .values(dicted_element)
                    )
                self.data[element.id].update(dicted_element)
                update_info.append("Updated")
            if "Updated" not in update_info:
                HTTPabort(404, "No elements to update")
            self.resort()
            return update_info

    async def get_all(self) -> list:
        return self.sorted_list

    async def get_customers(self) -> list:
        async with self.lock:
            result = {"all": len(self.data), "people": {}}
            by_customers = {}
            for anime in self.data.values():
                customers = (anime["order_by"] or cfg.STREAMER).split("+")
                for customer in customers:
                    if customer not in by_customers:
                        by_customers[customer] = {
                            "list": [],
                            "count": 0,
                        }
                    status = f"({anime['status']})" if anime["status"] else ""
                    by_customers[customer]["list"].append(
                        (f"{anime['series'] or ''} {anime['name']} {status}").strip()
                    )
                    by_customers[customer]["count"] += 1
            for customer, info in by_customers.items():
                by_customers[customer]["list"] = sorted(
                    info["list"], key=lambda anime: anime.lower()
                )
            result["people"] = by_customers
            return result
