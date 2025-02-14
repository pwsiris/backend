from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import data_params as schema_data_params

router = APIRouter()


@router.get("/{name}")
async def get_data_param(name):
    return HTTPanswer(200, await all_data.DATAPARAMS.get(name))


@router.post("", dependencies=[Depends(login_admin_required)])
@router.post("/", dependencies=[Depends(login_admin_required)])
async def add_data_param(
    data_param: schema_data_params.Element,
    session=Depends(get_session),
):
    await all_data.DATAPARAMS.add(session, data_param)
    return HTTPanswer(201, "Added")


@router.put("", dependencies=[Depends(login_admin_required)])
@router.put("/", dependencies=[Depends(login_admin_required)])
async def update_data_param(
    data_param: schema_data_params.Element,
    session=Depends(get_session),
):
    await all_data.DATAPARAMS.update(session, data_param)
    return HTTPanswer(200, "Updated")


@router.delete("", dependencies=[Depends(login_admin_required)])
@router.delete("/", dependencies=[Depends(login_admin_required)])
async def delete_data_param(
    data_param: schema_data_params.ElementName,
    session=Depends(get_session),
):
    await all_data.DATAPARAMS.delete(session, data_param.name)
    return HTTPanswer(200, "Deleted")


@router.get("/reset", dependencies=[Depends(login_admin_required)])
async def reset_data_params(session=Depends(get_session)):
    await all_data.DATAPARAMS.reset(session)
    return HTTPanswer(200, "Data Params were erased")
