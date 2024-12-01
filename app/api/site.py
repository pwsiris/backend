import httpx
from common.all_data import all_data
from common.config import cfg
from fastapi import APIRouter, Depends
from schemas import site as schema_site

from . import HTTPanswer, login_admin_required, token_messages_required

router = APIRouter()


@router.post("/message", dependencies=[Depends(token_messages_required)])
async def site_message(message: schema_site.Message):
    if not all_data.SITE_MESSAGES_ENABLED:
        return HTTPanswer(200, "DISABLED")

    async with httpx.AsyncClient() as ac:
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
async def site_message_enabled(enabled: schema_site.Enabled):
    all_data.SITE_MESSAGES_ENABLED = enabled.value
    return HTTPanswer(200, f"Set to {enabled.value}")


@router.put("/message/title", dependencies=[Depends(login_admin_required)])
async def update_message_title(title: schema_site.Title):
    all_data.SITE_MESSAGES_TITLE_TEXT = title.text
    all_data.SITE_MESSAGES_TITLE_EDITABLE = title.editable
    return HTTPanswer(200, "Message title params were changed")


@router.get("/message/title")
async def get_message_title():
    return HTTPanswer(
        200,
        {
            "text": all_data.SITE_MESSAGES_TITLE_TEXT,
            "editable": all_data.SITE_MESSAGES_TITLE_EDITABLE,
        },
    )
