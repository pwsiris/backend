from common.all_data import all_data
from db.utils import get_session
from fastapi import APIRouter, Depends, Query
from schemas import games as schema_games

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("")
@router.get("/")
async def get_games(types: list[str] = Query([])):
    return HTTPanswer(200, await all_data.GAMES.get_all(types))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_games(
    elements: list[schema_games.NewElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        201,
        await all_data.GAMES.add(session, elements),
    )


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_games(
    elements: list[schema_games.UpdatedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.GAMES.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_games(
    elements: list[schema_games.DeletedElement],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.GAMES.delete(session, elements),
        },
    )


@router.get("/genres")
async def get_genres(genre: str = Query("")):
    return HTTPanswer(200, await all_data.GAMES.get_genres(genre))


@router.put("/genres", dependencies=[Depends(login_admin_required)])
async def update_genres(
    elements: list[schema_games.UpdatedGenre],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.GAMES.update_genres(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_games(session=Depends(get_session)):
    await all_data.GAMES.reset(session)
    return HTTPanswer(200, "Games were erased")


@router.get("/customers", dependencies=[Depends(login_admin_required)])
async def games_customers():
    return HTTPanswer(200, await all_data.GAMES.get_customers())
