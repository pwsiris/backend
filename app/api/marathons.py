from common.all_data import all_data
from db.utils import get_session
from fastapi import APIRouter, Depends
from schemas import marathons as marathons_games

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_marathons():
    return HTTPanswer(200, await all_data.MARATHONS.get_all())


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_marathons(
    elements: list[marathons_games.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.MARATHONS.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_marathons(
    elements: list[marathons_games.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.MARATHONS.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_marathons(
    elements: list[marathons_games.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.MARATHONS.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_marathons(session=Depends(get_session)):
    await all_data.MARATHONS.reset(session)
    return HTTPanswer(200, "Marathons were erased")
