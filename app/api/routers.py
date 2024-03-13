from fastapi import APIRouter

from .admin import router as admin_router
from .anime import router as anime_router
from .challenges import router as challenges_router
from .games import router as games_router
from .lore import router as lore_router
from .marathons import router as marathons_router
from .socials import router as socials_router
from .twitchbot import router as twitchbot_router
from .twitchbot_service import router as twitchbot_service_router

routers = APIRouter()

routers.include_router(admin_router, prefix="/admin")
routers.include_router(anime_router, prefix="/anime")
routers.include_router(challenges_router, prefix="/challenges")
routers.include_router(games_router, prefix="/games")
routers.include_router(lore_router, prefix="/lore")
routers.include_router(marathons_router, prefix="/marathons")
routers.include_router(socials_router, prefix="/socials")
routers.include_router(twitchbot_router, prefix="/twitchbot")
routers.include_router(twitchbot_service_router, prefix="/twitchbot_service")
