from common.all_data import all_data
from db.utils import get_session
from fastapi import APIRouter, Depends
from schemas import lore as schema_lore

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_lore():
    return HTTPanswer(200, await all_data.LORE.get_all())


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_lore(
    elements: list[schema_lore.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.LORE.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_lore(
    elements: list[schema_lore.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.LORE.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_lore(
    elements: list[schema_lore.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.LORE.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_lore(session=Depends(get_session)):
    await all_data.LORE.reset(session)
    return HTTPanswer(200, "Lore was erased")
