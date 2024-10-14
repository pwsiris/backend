from common.all_data import all_data
from db.utils import get_session
from fastapi import APIRouter, Depends
from schemas import merch as schema_merch

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_merch():
    return HTTPanswer(200, await all_data.MERCH.get_all())


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_merch(
    elements: list[schema_merch.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.MERCH.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_merch(
    elements: list[schema_merch.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.MERCH.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_merch(
    elements: list[schema_merch.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.MERCH.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_merch(session=Depends(get_session)):
    await all_data.MERCH.reset(session)
    return HTTPanswer(200, "Merch was erased")


@router.put("/status", dependencies=[Depends(login_admin_required)])
async def change_status_merch(status: schema_merch.Status):
    all_data.MERCH.set_status(status.status)
    return HTTPanswer(200, "Merch status was updated")


@router.get("/status")
async def get_status_merch():
    return HTTPanswer(200, all_data.MERCH.get_status())
