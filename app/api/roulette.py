from common.all_data import all_data
from db.utils import get_session
from fastapi import APIRouter, Depends
from schemas import roulette as schema_roulette

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_awards():
    return HTTPanswer(200, await all_data.ROULETTE.get_all())


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_awards(
    elements: list[schema_roulette.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.ROULETTE.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_awards(
    elements: list[schema_roulette.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.ROULETTE.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_awards(
    elements: list[schema_roulette.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.ROULETTE.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_awards(session=Depends(get_session)):
    await all_data.ROULETTE.reset(session)
    return HTTPanswer(200, "Roulette awards were erased")
