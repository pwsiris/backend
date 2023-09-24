from common.all_data import all_data
from db.utils import get_session
from fastapi import APIRouter, Depends
from schemas import anime as schema_anime

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_anime():
    return HTTPanswer(200, await all_data.ANIME.get_all())


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_anime(
    elements: list[schema_anime.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.ANIME.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_anime(
    elements: list[schema_anime.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.ANIME.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_anime(
    elements: list[schema_anime.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.ANIME.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_anime(session=Depends(get_session)):
    await all_data.ANIME.reset(session)
    return HTTPanswer(200, "Anime were erased")


@router.get("/customers", dependencies=[Depends(login_admin_required)])
async def anime_customers():
    return HTTPanswer(200, await all_data.ANIME.get_customers())
