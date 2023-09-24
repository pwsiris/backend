from typing import Any

from common.config import cfg
from fastapi import HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse


async def verify_twitchbot_token(token: str = Query("")) -> None:
    if token != cfg.TWITCHBOT_TOKEN:
        raise HTTPException(status_code=401, detail="NO AUTH")


async def login_admin_required(request: Request) -> None:
    token_cookie = request.cookies.get(cfg.AUTH_TOKEN_NAME)
    token_header = request.headers.get(cfg.AUTH_TOKEN_NAME)

    if (
        token_cookie != cfg.AUTH_ADMIN_TMP_TOKEN
        and token_header != cfg.AUTH_ADMIN_TMP_TOKEN
    ):
        raise HTTPException(status_code=401, detail="NO AUTH")


def HTTPanswer(
    status_code: int,
    description: Any,
    action_cookie: str | None = None,
    token: str | None = None,
) -> JSONResponse:
    response = JSONResponse(
        status_code=status_code,
        content={"content": description},
    )
    if action_cookie == "set":
        response.set_cookie(
            key=cfg.AUTH_TOKEN_NAME,
            value=token,
            path="/",
            domain=cfg.DOMAIN,
            httponly=True,
            secure=(True if cfg.ENV != "dev" else False),
            samesite=("strict" if cfg.ENV != "dev" else "lax"),
        )
    elif action_cookie == "delete":
        response.delete_cookie(cfg.AUTH_TOKEN_NAME, path="/", domain=cfg.DOMAIN)

    return response


def PlainAnswer(description: str) -> Response:
    return Response(content=description, media_type="text/html")
