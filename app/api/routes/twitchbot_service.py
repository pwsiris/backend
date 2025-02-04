from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from common.errors import HTTPabort
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import twitchbot as schema_twitchbot

router = APIRouter()


@router.put("/timecode-answer", dependencies=[Depends(login_admin_required)])
async def timecode_text(new_answer: schema_twitchbot.TimecodeAnswer):
    all_data.TIMECODE_MESSAGE = new_answer.value
    return HTTPanswer(200, "Timecode answer was changed")


@router.put("/cheats", dependencies=[Depends(login_admin_required)])
async def cheating(cheats: schema_twitchbot.Cheats):
    if cheats.streamer:
        all_data.BITE_CHEAT_STREAMER_PERCENT = cheats.streamer
    if cheats.defense:
        all_data.BITE_CHEAT_DEFENSE_PERCENT = cheats.defense
    return HTTPanswer(200, f"were set to {cheats.model_dump(exclude_none=True)}")


@router.get("/cheats", dependencies=[Depends(login_admin_required)])
async def cheating_info():
    return HTTPanswer(
        200,
        {
            "streamer": all_data.BITE_CHEAT_STREAMER_PERCENT,
            "defense": all_data.BITE_CHEAT_DEFENSE_PERCENT,
        },
    )


@router.get("/reset-lists", dependencies=[Depends(login_admin_required)])
async def reset_lists(session=Depends(get_session)):
    await all_data.SAVE_CHOICES.reset_all(session)
    return HTTPanswer(200, "All lists were erased")


@router.get("/reset-counters", dependencies=[Depends(login_admin_required)])
async def reset_counters(session=Depends(get_session)):
    await all_data.COUNTER.reset_all(session)
    return HTTPanswer(200, "All counters were erased")


@router.get("/{category}", dependencies=[Depends(login_admin_required)])
async def get_all_elements(category: str, raw: bool = False):
    if not all_data.is_twitchbot(category):
        HTTPabort(404, "Category not found")

    return HTTPanswer(200, await getattr(all_data, category.upper()).get_all(raw))


@router.post("/{category}", dependencies=[Depends(login_admin_required)])
async def add_elements(
    category: str,
    elements: list[schema_twitchbot.NewElement],
    session=Depends(get_session),
):
    if not all_data.has_list(category):
        HTTPabort(404, "Category not found")

    return HTTPanswer(
        200, await getattr(all_data, category.upper()).add(session, elements)
    )


@router.put("/{category}", dependencies=[Depends(login_admin_required)])
async def update_elements(
    category: str,
    elements: list[schema_twitchbot.UpdatedElement],
    session=Depends(get_session),
):
    if not all_data.has_list(category):
        HTTPabort(404, "Category not found")

    await getattr(all_data, category.upper()).update(session, elements)
    return HTTPanswer(200, "Elements were updated")


@router.delete("/{category}", dependencies=[Depends(login_admin_required)])
async def delete_elements(
    category: str,
    elements: list[schema_twitchbot.DeletedElement],
    session=Depends(get_session),
):
    if not all_data.has_list(category):
        HTTPabort(404, "Category not found")

    await getattr(all_data, category.upper()).delete(session, elements)
    return HTTPanswer(200, "Elements were deleted")


@router.get("/{category}/reset", dependencies=[Depends(login_admin_required)])
async def reset(category: str, session=Depends(get_session)):
    if not all_data.is_twitchbot(category):
        HTTPabort(404, "Category not found")

    await getattr(all_data, category.upper()).reset(session)
    return HTTPanswer(200, "Elemets were resetted")
