from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import data_params as schema_data_params

router = APIRouter()


@router.get("/{name}")
async def get_data_param(name):
    return HTTPanswer(200, all_data.DATA_PARAMS.get(name))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_data_params(
    elements: list[schema_data_params.Element],
    session=Depends(get_session),
):
    return HTTPanswer(201, await all_data.DATA_PARAMS.add(session, elements))


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_data_params(
    elements: list[schema_data_params.Element],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Update info",
            "info": await all_data.DATA_PARAMS.update(session, elements),
        },
    )


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_data_params(
    elements: list[schema_data_params.ElementName],
    session=Depends(get_session),
):
    return HTTPanswer(
        200,
        {
            "status": "Delete info",
            "info": await all_data.DATA_PARAMS.delete(session, elements),
        },
    )


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_data_params(session=Depends(get_session)):
    await all_data.DATA_PARAMS.reset(session)
    return HTTPanswer(200, "Data Params were erased")
