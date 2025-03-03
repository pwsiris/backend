import random
from datetime import datetime

import httpx
from api.answers import PlainAnswer
from api.verification import verify_twitchbot_token
from common.all_data import all_data
from common.config import cfg
from db.common import get_session
from fastapi import APIRouter, Depends, Query

router = APIRouter()


@router.get("/timecode", dependencies=[Depends(verify_twitchbot_token)])
async def timecode(
    title: str, uptime: str, user_name: str, game: str, description: str
):
    message = all_data.DATAPARAMS.get("TIMECODE_MESSAGE")
    async with httpx.AsyncClient() as ac:
        json = {
            "embeds": [
                {
                    "title": title,
                    "fields": [
                        {"name": "Timecode", "value": uptime, "inline": True},
                        {"name": "Sender", "value": user_name, "inline": True},
                    ],
                    "footer": {"text": game},
                }
            ]
        }
        for prefix in ("!тк", "!tc", "!timecode"):
            description = description.replace(prefix, "")
            description = description.replace(prefix.capitalize(), "")
            description = description.replace(prefix.upper(), "")
        description = description.lstrip(" ")
        if description:
            json["embeds"][0]["description"] = description
        answer = await ac.post(cfg.DISCORD_HOOK_TIMECODE, json=json)
        if answer.status_code < 200 or answer.status_code >= 300:
            cfg.logger.error(answer.status_code)
            cfg.logger.error(answer.content)
            message = (
                f"Failed to send stream timecode to discord (code {answer.status_code})"
            )
    return PlainAnswer(message)


@router.get("/save_please", dependencies=[Depends(verify_twitchbot_token)])
async def save_please():
    return PlainAnswer(all_data.SAVE_CHOICES.get_random())


@router.get("/bite", dependencies=[Depends(verify_twitchbot_token)])
async def bite_someone(sender: str, targets: list[str] = Query([])):
    action = all_data.BITE_ACTIONS.get_random()
    place = all_data.BITE_PLACES.get_random()
    body_part = all_data.BITE_BODY_PARTS.get_random()

    target = cfg.STREAMER
    for variant in targets:
        if (
            not all_data.BITE_IGNORE_LIST.has(variant.lower().rstrip().lstrip())
            and variant.lower() != sender.lower()
        ):
            target = variant
            break

    random.seed(datetime.now().timestamp())
    if sender == cfg.BEST_MODERATOR and (
        random.randint(1, 100) <= all_data.DATAPARAMS.get("BITE_CHEAT_STREAMER_PERCENT")
    ):
        target = cfg.STREAMER

    message = f"Однажды тёмной ночью {sender} {action} в {place} к {target} и кусьнул за {body_part}"
    if target == cfg.BEST_MODERATOR and (
        random.randint(1, 100) <= all_data.DATAPARAMS.get("BITE_CHEAT_DEFENSE_PERCENT")
    ):
        message = f"Однажды тёмной ночью {sender} {action} в {place} к {target} и в проваленной попытке укусить получил леща в ответ"

    return PlainAnswer(message)


@router.get("/counter", dependencies=[Depends(verify_twitchbot_token)])
async def counter(
    user_level: str,
    name: str,
    description: str,
    type: str,
    session=Depends(get_session),
):
    def _list_get(list, index):
        if -1 < index < len(list):
            return list[index]
        else:
            return None

    name = name.lower()

    description = description.lstrip(" ").lower().split()[1:]
    description_str = " ".join(word for word in description)

    if type == "death":
        prefix = "Смертей"
        counter = all_data.COUNTER_DEATH
    elif type == "count":
        prefix = "Счётчик"
        counter = all_data.COUNTER

    if int(user_level) >= 500:  # moderators and upper in streamelements
        if _list_get(description, 0) in ("set", "установить"):
            try:
                new_value = int(_list_get(description, 1))
                result = await counter.set(session, name, new_value)
                return PlainAnswer(f"{prefix}: {result}")
            except Exception:
                return PlainAnswer("В команде нет корректного числа")

    if (value := await counter.get_value(description_str.lower(), None)) != None:
        return PlainAnswer(f"{prefix} в {description_str}: {value}")

    if _list_get(description, 0) in ("list", "список"):
        return PlainAnswer(await counter.get_all())

    if await counter.get_value(name, None) == None:
        return PlainAnswer("Нет счётчика")

    if _list_get(description, 0) in ("current", "текущая"):
        return PlainAnswer(f"{prefix} в {name}: {await counter.get_value(name, 'Нет')}")

    if description:
        return PlainAnswer("Ошибка в команде/названии/правах")

    result = await counter.update(session, name, True)
    if result in ("Нет счётчика", "Cлишком быстрое изменение счётчика"):
        return PlainAnswer(result)
    else:
        return PlainAnswer(f"{prefix}: {result}")


@router.get("/gcounter", dependencies=[Depends(verify_twitchbot_token)])
async def gcounter(
    user_level: str,
    description: str,
    session=Depends(get_session),
):
    description = description.lstrip(" ").split()[1:]

    if int(user_level) >= 500:  # moderators and upper in streamelements
        if len(description) == 2:
            try:
                new_value = int(description[1])
                result = await all_data.COUNTER_GLOBAL.set(
                    session, description[0], new_value
                )
                return PlainAnswer(f"{description[0]}: {result}")
            except Exception:
                return PlainAnswer("В команде нет корректного числа")

    if description:
        return PlainAnswer(
            await all_data.COUNTER_GLOBAL.get_value(description[0], "Нет")
        )

    return PlainAnswer("Ошибка в команде/названии/правах")


@router.get("/eat-rabbit", dependencies=[Depends(verify_twitchbot_token)])
async def eat_rabbit(
    name: str,
    message: str,
    session=Depends(get_session),
):
    rabbit_count = message.count(name)
    random.seed(datetime.now().timestamp())
    rabbits_saved = int((random.randint(0, 100) / 100) * rabbit_count)
    rabbits_stealed = rabbit_count - rabbits_saved

    result = await all_data.COUNTER_GLOBAL.update(session, name, False, rabbits_stealed)

    if result != "Нет счётчика":
        return PlainAnswer(
            f"украл(а) {rabbits_stealed} кролей"
            + (f" ({rabbits_saved} сбежало)" if rabbits_saved else "")
            + ". Всего украли: "
            + result
        )
    else:
        return PlainAnswer(result)


@router.get("/save-rabbit", dependencies=[Depends(verify_twitchbot_token)])
async def save_rabbit(
    name: str,
    session=Depends(get_session),
):
    random.seed(datetime.now().timestamp())
    rabbits = int(
        (random.randint(0, 100) / 100)
        * (await all_data.COUNTER_GLOBAL.get_value(name, 0))
    )

    result = await all_data.COUNTER_GLOBAL.update(session, name, False, -rabbits)
    if result != "Нет счётчика":
        return PlainAnswer(f"Кролей спасено: {rabbits}, осталось: " + result)
    else:
        return PlainAnswer(result)
