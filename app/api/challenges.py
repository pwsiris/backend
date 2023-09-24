from common.all_data import all_data
from db.utils import get_session
from fastapi import APIRouter, Depends, Query
from schemas import challenges as schema_challenges

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_challenges(types: list[str] = Query([])):
    return HTTPanswer(200, await all_data.CHALLENGES.get_all(types))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_challenges(
    elements: list[schema_challenges.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.CHALLENGES.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_challenges(
    elements: list[schema_challenges.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.CHALLENGES.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_challenges(
    elements: list[schema_challenges.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.CHALLENGES.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_challenges(session=Depends(get_session)):
    await all_data.CHALLENGES.reset(session)
    return HTTPanswer(200, "Challenges were erased")
