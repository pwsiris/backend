import httpx
from common.config import cfg
from fastapi import APIRouter, Body, Depends

from . import HTTPanswer, token_messages_required

router = APIRouter()


@router.post("/message", dependencies=[Depends(token_messages_required)])
async def site_message(title: str | None = Body(), description: str = Body()):
    title = title or ""
    description = description

    async with httpx.AsyncClient() as ac:
        json = {"embeds": [{"title": title, "description": description}]}
        answer = await ac.post(cfg.DISCORD_HOOK_SITE_MESSAGES, json=json)
        if answer.status_code < 200 or answer.status_code >= 300:
            return HTTPanswer(
                400,
                f"Failed to send stream timecode to discord (code {answer.status_code})",
            )
    return HTTPanswer(200, "Sended")
