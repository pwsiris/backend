from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import auctions as schema_auctions

router = APIRouter()


@router.get("")
@router.get("/")
async def get_auctions(raw: bool = False):
    return HTTPanswer(200, await all_data.AUCTIONS.get_all(raw))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_auctions(
    elements: list[schema_auctions.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.AUCTIONS.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_auctions(
    elements: list[schema_auctions.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.AUCTIONS.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_auctions(
    elements: list[schema_auctions.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.AUCTIONS.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_auctions(session=Depends(get_session)):
    await all_data.AUCTIONS.reset(session)
    return HTTPanswer(200, "Auctions were erased")
