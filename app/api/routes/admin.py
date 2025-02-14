import json
from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile

from api.answers import HTTPanswer
from api.verification import login_admin_required
from common.all_data import all_data
from common.config import cfg
from common.errors import HTTPabort
from fastapi import APIRouter, Depends, Response
from schemas import admin as schema_admin

router = APIRouter()


@router.get("/secrets", dependencies=[Depends(login_admin_required)])
async def secrets_update():
    error = await cfg.load_secrets_async()
    if error:
        HTTPabort(400, error)
    no_secrets = cfg.apply_secrets(get_db=False)
    return HTTPanswer(200, {"Not updated": no_secrets})


@router.put("/secrets", dependencies=[Depends(login_admin_required)])
async def secrets_creds(updated_creds: schema_admin.UpdatedCreds):
    await cfg.update_creds(updated_creds.model_dump(exclude_none=True))
    return HTTPanswer(200, "Updated")


@router.get("/dump", dependencies=[Depends(login_admin_required)])
async def get_dump():
    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "a") as zip_file:
        for name in (
            "save_choices",
            "bite_ignore_list",
            "bite_actions",
            "bite_places",
            "bite_body_parts",
        ):
            data = await getattr(all_data, name.upper()).get_all(raw=True)
            data_rows = "\n".join(data.split("|||||"))
            zip_file.writestr(f"{name}.txt", data_rows)

        for name in ("counter", "counter_death", "counter_global"):
            data = await getattr(all_data, name.upper()).get_all(raw=True)
            zip_file.writestr(f"{name}.txt", data)

        for name in (
            "anime",
            "auctions",
            "challenges",
            "credits",
            "dataparams" "games",
            "lore",
            "marathons",
            "merch",
            "roulette",
            "socials",
        ):
            data = await getattr(all_data, name.upper()).get_all(raw=True)
            zip_file.writestr(
                f"{name}.json", json.dumps(data, ensure_ascii=False, indent=4)
            )

    zip_buffer.seek(0)
    current_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    return Response(
        zip_buffer.getvalue(),
        headers={"filename": f"pwsi_{cfg.ENV}_{current_datetime}.zip"},
        media_type="application/zip",
    )
