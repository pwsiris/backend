from typing import Any

from common.config import cfg
from fastapi import Response
from fastapi.responses import JSONResponse


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
