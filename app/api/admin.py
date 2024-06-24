from common.config import cfg
from common.errors import HTTPabort
from fastapi import APIRouter, Depends
from schemas import admin as schema_admin

from . import HTTPanswer, login_admin_required

router = APIRouter()


@router.get("/secrets", dependencies=[Depends(login_admin_required)])
async def secrets_update():
    error, secrets_data = await cfg.load_secrets_async()
    if error:
        HTTPabort(400, error)
    no_secrets = cfg.get_secrets(secrets_data, get_db=False)
    return HTTPanswer(200, {"Not updated": no_secrets})


@router.put("/secrets", dependencies=[Depends(login_admin_required)])
async def secrets_creds(updated_creds: schema_admin.UpdatedCreds):
    await cfg.update_creds(updated_creds)
    return HTTPanswer(200, "Updated")
