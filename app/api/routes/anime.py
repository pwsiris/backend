from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import anime as schema_anime

router = APIRouter()


@router.get("")
@router.get("/")
async def get_anime(raw: bool = False):
    return HTTPanswer(200, await all_data.ANIME.get_all(raw))


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


@router.post("/pictures", dependencies=[Depends(login_admin_required)])
async def update_stream_pictures(
    elements: list[int] = [],
    session=Depends(get_session),
):
    return HTTPanswer(200, await all_data.ANIME.update_pictures(session, elements))
