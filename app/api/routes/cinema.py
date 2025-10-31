from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Body, Depends, Query
from schemas import cinema as schema_cinema

router = APIRouter()


@router.get("")
@router.get("/")
async def get_cinema(raw: bool = False, types: list[str] = Query([])):
    return HTTPanswer(200, await all_data.CINEMA.get_all(raw, types))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_cinema(
    elements: list[schema_cinema.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.CINEMA.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_cinema(
    elements: list[schema_cinema.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.CINEMA.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_cinema(
    elements: list[schema_cinema.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.CINEMA.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_cinema(session=Depends(get_session)):
    await all_data.CINEMA.reset(session)
    return HTTPanswer(200, "Cinema were erased")


@router.get("/types")
async def get_types():
    return HTTPanswer(200, await all_data.CINEMA.get_types())


@router.put("/types")
async def set_default_types_order(elements: list[str] = Body()):
    await all_data.CINEMA.set_default_types_order(elements)
    return HTTPanswer(200, "New default order was set and cinema was resorted")


@router.get("/customers", dependencies=[Depends(login_admin_required)])
async def cinema_customers():
    return HTTPanswer(200, await all_data.CINEMA.get_customers())
