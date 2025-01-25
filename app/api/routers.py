from api.routes.admin import router as admin_router
from api.routes.anime import router as anime_router
from api.routes.auctions import router as auctions_router
from api.routes.challenges import router as challenges_router
from api.routes.credits import router as credits_router
from api.routes.games import router as games_router
from api.routes.lore import router as lore_router
from api.routes.marathons import router as marathons_router
from api.routes.merch import router as merch_router
from api.routes.roulette import router as roulette_router
from api.routes.site import router as site_router
from api.routes.socials import router as socials_router
from api.routes.twitchbot import router as twitchbot_router
from api.routes.twitchbot_service import router as twitchbot_service_router
from fastapi import APIRouter
from versions import APP_VERSION_DICT

routers = APIRouter()

routers.include_router(admin_router, prefix="/admin")
routers.include_router(anime_router, prefix="/anime")
routers.include_router(auctions_router, prefix="/auctions")
routers.include_router(challenges_router, prefix="/challenges")
routers.include_router(credits_router, prefix="/credits")
routers.include_router(games_router, prefix="/games")
routers.include_router(lore_router, prefix="/lore")
routers.include_router(marathons_router, prefix="/marathons")
routers.include_router(merch_router, prefix="/merch")
routers.include_router(roulette_router, prefix="/roulette")
routers.include_router(site_router, prefix="/site")
routers.include_router(socials_router, prefix="/socials")
routers.include_router(twitchbot_router, prefix="/twitchbot")
routers.include_router(twitchbot_service_router, prefix="/twitchbot_service")


@routers.get("/version")
def get_version():
    return APP_VERSION_DICT
