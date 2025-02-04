from common.config import cfg
from fastapi import HTTPException, Query, Request


async def verify_twitchbot_token(token: str = Query("")) -> None:
    if token != cfg.TWITCHBOT_TOKEN:
        raise HTTPException(status_code=401, detail="NO AUTH")


async def token_messages_required(request: Request) -> None:
    token_header = request.headers.get("X-SITE-MESSAGES-TOKEN")

    if token_header != cfg.AUTH_SITE_MESSAGES_TMP_TOKEN:
        raise HTTPException(status_code=401, detail="NO AUTH")


async def login_admin_required(request: Request) -> None:
    token_cookie = request.cookies.get(cfg.AUTH_TOKEN_NAME)
    token_header = request.headers.get(cfg.AUTH_TOKEN_NAME)

    if (
        token_cookie != cfg.AUTH_ADMIN_TMP_TOKEN
        and token_header != cfg.AUTH_ADMIN_TMP_TOKEN
    ):
        raise HTTPException(status_code=401, detail="NO AUTH")
