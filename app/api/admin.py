from common.config import cfg
from fastapi import APIRouter, Depends
from schemas import admin as schema_admin

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("/secrets", dependencies=[Depends(login_admin_required)])
async def secrets_update():
    return HTTPanswer(200, {"Not updated": await cfg.get_secrets(False)})


@router.put("/secrets", dependencies=[Depends(login_admin_required)])
async def secrets_creds(updated_creds: schema_admin.UpdatedCreds):
    await cfg.update_creds(updated_creds)
    return HTTPanswer(200, "Updated")
