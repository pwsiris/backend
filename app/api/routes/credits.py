from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import credits as schema_credits

router = APIRouter()


@router.get("")
@router.get("/")
async def get_credits(raw: bool = False):
    return HTTPanswer(200, await all_data.CREDITS.get_all(raw))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_credits(
    elements: list[schema_credits.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.CREDITS.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_credits(
    elements: list[schema_credits.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.CREDITS.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_credits(
    elements: list[schema_credits.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.CREDITS.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_credits(session=Depends(get_session)):
    await all_data.CREDITS.reset(session)
    return HTTPanswer(200, "Credits were erased")
