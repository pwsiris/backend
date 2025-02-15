from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import marathons as schema_marathons

router = APIRouter()


@router.get("")
@router.get("/")
async def get_marathons(raw: bool = False):
    return HTTPanswer(200, await all_data.MARATHONS.get_all(raw))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_marathons(
    elements: list[schema_marathons.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.MARATHONS.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_marathons(
    elements: list[schema_marathons.UpdatedElement],
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
    elements: list[schema_marathons.DeletedElement],
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
