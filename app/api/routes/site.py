import httpx
from api.answers import HTTPanswer
from api.verification import login_admin_required, token_messages_required
from common.all_data import all_data
from common.config import cfg
from db.common import get_session
from fastapi import APIRouter, Depends
from schemas import data_params as schema_data_params
from schemas import site as schema_site

router = APIRouter()


@router.post("/message", dependencies=[Depends(token_messages_required)])
async def site_message(message: schema_site.Message):
    if not all_data.DATA_PARAMS.get("SITE_MESSAGES_ENABLED"):
        return HTTPanswer(200, "DISABLED")

    async with httpx.AsyncClient() as ac:
        # json = {"content": f"{message.title or ''}\n\n{message.description}".strip()}
        json = {
            "embeds": [
                {"title": message.title or "", "description": message.description}
            ]
        }
        answer = await ac.post(cfg.DISCORD_HOOK_SITE_MESSAGES, json=json)
        if answer.status_code < 200 or answer.status_code >= 300:
            return HTTPanswer(
                400,
                f"Failed to send stream timecode to discord (code {answer.status_code})",
            )
    return HTTPanswer(200, "Sended")


@router.put("/message", dependencies=[Depends(login_admin_required)])
async def site_message_enabled(
    enabled: schema_site.Enabled, session=Depends(get_session)
):
    await all_data.DATA_PARAMS.update(
        session,
        [
            schema_data_params.Element(
                name="SITE_MESSAGES_ENABLED", value_bool=enabled.value
            )
        ],
    )
    return HTTPanswer(200, f"Set to {enabled.value}")


@router.put("/message/title", dependencies=[Depends(login_admin_required)])
async def update_message_title(title: schema_site.Title, session=Depends(get_session)):
    await all_data.DATA_PARAMS.update(
        session,
        [
            schema_data_params.Element(
                name="SITE_MESSAGES_TITLE_TEXT", value_str=title.text
            )
        ],
    )
    await all_data.DATA_PARAMS.update(
        session,
        [
            schema_data_params.Element(
                name="SITE_MESSAGES_TITLE_VISIBLE", value_bool=title.visible
            )
        ],
    )
    await all_data.DATA_PARAMS.update(
        session,
        [
            schema_data_params.Element(
                name="SITE_MESSAGES_TITLE_EDITABLE", value_str=title.editable
            )
        ],
    )
    return HTTPanswer(200, "Message title params were changed")


@router.get("/message/title")
async def get_message_title():
    return HTTPanswer(
        200,
        {
            "text": all_data.DATA_PARAMS.get("SITE_MESSAGES_TITLE_TEXT"),
            "visible": all_data.DATA_PARAMS.get("SITE_MESSAGES_TITLE_VISIBLE"),
            "editable": all_data.DATA_PARAMS.get("SITE_MESSAGES_TITLE_EDITABLE"),
        },
    )
