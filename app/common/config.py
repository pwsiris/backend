import sys
from time import sleep

import httpx
import requests
import yaml
from aiofile import async_open
from common.utils import (
    disable_unnecessary_loggers,
    get_args,
    get_logger,
    levelDEBUG,
    levelINFO,
)


class ConfigManager:
    def __init__(self) -> None:
        self._config_file = "config/config.yaml"

        self.secrets_data = {}
        args = get_args()
        self.ENV = args.env

        if self.ENV != "dev":
            disable_unnecessary_loggers()

        self.logger = get_logger(levelDEBUG if self.ENV == "dev" else levelINFO)

        self.load_creds_sync()
        error = self.get_creds()
        if error:
            self.logger.error(error)
            sys.exit(1)
        self.logger.info("Creds from config were loaded")

        error = self.load_secrets_sync()
        if error:
            self.logger.error(error)
            self.logger.error("waiting 120 secs for secrets storage")
            sleep(120)
            error = self.load_secrets_sync()
        if error:
            self.logger.error(error)
            sys.exit(1)

        no_secrets = self.apply_secrets(get_db=True)
        if no_secrets:
            self.logger.error(f"No secrets found: {no_secrets}")
            sys.exit(1)
        self.logger.info("Secrets were loaded")

    def load_creds_sync(self) -> None:
        with open(self._config_file, "r") as f:
            self.creds_data = yaml.safe_load(f.read())

    async def load_creds_async(self) -> None:
        async with async_open(self._config_file, "r") as f:
            self.creds_data = yaml.safe_load(await f.read())

    def get_creds(self) -> str:
        try:
            self.SECRETS_DOMAIN = self.creds_data["secrets_domain"] or ""
            self.SECRETS_HEADER = self.creds_data["secrets_header"] or ""
            self.SECRETS_TOKEN = self.creds_data["secrets_token"] or ""
        except Exception:
            return "Error getting secrets creds from config-file"
        return ""

    async def update_creds(self, updated_creds: dict) -> None:
        self.creds_data.update(updated_creds.model_dump(exclude_none=True))

        self.SECRETS_DOMAIN = self.creds_data["secrets_domain"]
        self.SECRETS_HEADER = self.creds_data["secrets_header"]
        self.SECRETS_TOKEN = self.creds_data["secrets_token"]

        async with async_open(self._config_file, "w") as f:
            yaml.dump(self.creds_data, f)

    def load_secrets_sync(self) -> str:
        try:
            response = requests.get(
                f"{self.SECRETS_DOMAIN}/api/secrets",
                headers={self.SECRETS_HEADER: self.SECRETS_TOKEN},
            )
            if response.status_code != 200:
                return (
                    f"Error getting data from secrets response - {response.status_code}"
                )
        except Exception as e:
            return f"Error getting data from secrets - {e}"

        try:
            self.secrets_data = response.json()["content"]
            return ""
        except Exception:
            return "Error getting secrets from response"

    async def load_secrets_async(self) -> str:
        try:
            async with httpx.AsyncClient(
                base_url=self.SECRETS_DOMAIN,
                headers={self.SECRETS_HEADER: self.SECRETS_TOKEN},
            ) as ac:
                response = await ac.get("/api/secrets")
                if response.status_code != 200:
                    return f"Error getting data from secrets response - {response.status_code}"
        except Exception as e:
            return f"Error getting data from secrets - {e}"

        try:
            self.secrets_data = response.json()["content"]
            return ""
        except Exception:
            return "Error getting secrets from response"

    def apply_secrets(self, get_db: bool) -> list[str]:
        no_secrets = []

        # database: need to get only at startup
        if get_db:
            db_data = self.secrets_data.get(f"{self.ENV}/db/postgres")
            try:
                self.DB_CONNECTION_STRING = "{}://{}:{}@{}:{}/{}".format(
                    "postgresql+asyncpg",
                    db_data["user"],
                    db_data["password"],
                    db_data["host"],
                    str(db_data["port"]),
                    db_data["database"],
                )
            except Exception:
                no_secrets.append(f"{self.ENV}/db/postgres")

            # db_data = self.secrets_data.get(f"{self.ENV}/db")
            # try:
            #     self.DB_CONNECTION_STRING: str = db_data["connection string"]
            # except Exception:
            #     no_secrets.append(f"{self.ENV}/db")

        # initial admin credentials
        admin_data = self.secrets_data.get(f"{self.ENV}/admin")
        try:
            self.ADMIN_LOGIN = admin_data["login"]
            self.ADMIN_PASSWORD = admin_data["password"]
        except Exception:
            no_secrets.append(f"{self.ENV}/admin")

        # domain
        domain_data = self.secrets_data.get(f"{self.ENV}/domain")
        try:
            self.DOMAIN = domain_data["domain"]
        except Exception:
            no_secrets.append(f"{self.ENV}/domain")

        # auth service info
        auth_data = self.secrets_data.get(f"{self.ENV}/auth")
        try:
            self.AUTH_TOKEN_NAME = auth_data["token_name"]
            self.AUTH_TOKEN_KEY = auth_data["token_key"]
            self.AUTH_TOKEN_EXPIRE = auth_data["expire"]
            self.AUTH_ADMIN_TMP_TOKEN = auth_data["admin_tmp_token"]
            self.AUTH_SITE_MESSAGES_TMP_TOKEN = auth_data["site_messages_tmp_token"]
        except Exception:
            no_secrets.append(f"{self.ENV}/auth")

        # streamer name
        streamer_data = self.secrets_data.get(f"{self.ENV}/streamer")
        try:
            self.STREAMER = streamer_data["name"]
        except Exception:
            no_secrets.append(f"{self.ENV}/streamer")

        # moderator name
        moderator_data = self.secrets_data.get(f"{self.ENV}/moderator")
        try:
            self.BEST_MODERATOR = moderator_data["name"]
        except Exception:
            no_secrets.append(f"{self.ENV}/moderator")

        # twitch
        twitch_data = self.secrets_data.get(f"{self.ENV}/twitch")
        try:
            self.TWITCHBOT_TOKEN = twitch_data["bot_token"]
        except Exception:
            no_secrets.append(f"{self.ENV}/twitch")

        # discord hooks
        discord_data = self.secrets_data.get(f"{self.ENV}/discord")
        try:
            self.DISCORD_HOOK_TIMECODE = discord_data["hook_timecode"]
            self.DISCORD_HOOK_SITE_MESSAGES = discord_data["hook_site_messages"]
        except Exception:
            no_secrets.append(f"{self.ENV}/discord")

        # mal api
        mal_data = self.secrets_data.get(f"{self.ENV}/mal")
        try:
            self.MAL_API = mal_data["api_url"]
            self.MAL_HEADER = mal_data["header"]
            self.MAL_CLIENT_ID = mal_data["client_id"]
        except Exception:
            no_secrets.append(f"{self.ENV}/mal")

        return no_secrets


cfg = ConfigManager()
