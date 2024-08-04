from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import socials as schema_socials

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_socials():
    return HTTPanswer(200, await all_data.SOCIALS.get_all())


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_socials(
    elements: list[schema_socials.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.SOCIALS.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_socials(
    elements: list[schema_socials.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.SOCIALS.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_socials(
    elements: list[schema_socials.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.SOCIALS.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_socials(session=Depends(get_session)):
    await all_data.SOCIALS.reset(session)
    return HTTPanswer(200, "Socials were erased")
