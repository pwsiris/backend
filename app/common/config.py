import httpx
import yaml
from aiofile import async_open
from schemas.admin import UpdatedCreds

from .errors import HTTPabort


class ConfigManager:
    def __init__(self) -> None:
        self._config_file = "config/config.yaml"

    async def get_creds(self, env: str) -> None:
        self.ENV = env
        async with async_open(self._config_file, "r") as f:
            self.data = yaml.safe_load(await f.read())
            try:
                self.SECRETS_DOMAIN = self.data["secrets_domain"]
                self.SECRETS_HEADER = self.data["secrets_header"]
                self.SECRETS_TOKEN = self.data["secrets_token"]
            except Exception:
                print("Error getting secrets creds from config-file")
                raise

    async def update_creds(self, updated_creds: UpdatedCreds) -> None:
        self.data.update(updated_creds.model_dump(exclude_none=True))

        self.SECRETS_DOMAIN = self.data["secrets_domain"]
        self.SECRETS_HEADER = self.data["secrets_header"]
        self.SECRETS_TOKEN = self.data["secrets_token"]

        async with async_open(self._config_file, "w") as f:
            yaml.dump(self.data, f)

    async def get_secrets(self, initial: bool) -> None:
        try:
            async with httpx.AsyncClient(
                base_url=self.SECRETS_DOMAIN,
                params={"search": f"{self.ENV}/"},
                headers={self.SECRETS_HEADER: self.SECRETS_TOKEN},
            ) as ac:
                response = await ac.get("/api/secrets")
                if response.status_code != 200:
                    print(f"Error getting data from secrets - {response.status_code}")
                    if initial:
                        raise
                    else:
                        HTTPabort(
                            400,
                            {
                                "status_code": response.status_code,
                                "body": response.json(),
                            },
                        )
        except Exception as e:
            print(f"Error getting data from secrets - {e}")
            if initial:
                raise
            else:
                HTTPabort(400, str(e))

        secrets_data = response.json()["content"]

        no_secrets = []

        # postgres
        postgres_data = secrets_data.get(f"{self.ENV}/db/postgres")
        if postgres_data:
            self.DB_CONNECTION_STRING = "{}://{}:{}@{}:{}/{}".format(
                "postgresql+asyncpg",
                postgres_data["user"],
                postgres_data["password"],
                postgres_data["host"],
                str(postgres_data["port"]),
                postgres_data["database"],
            )
        else:
            print("No postgres data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/db/postgres")

        # initial admin credentials
        admin_data = secrets_data.get(f"{self.ENV}/admin")
        if admin_data:
            self.ADMIN_LOGIN = admin_data["login"]
            self.ADMIN_PASSWORD = admin_data["password"]
        else:
            print("No admin data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/admin")

        # domain
        domain_data = secrets_data.get(f"{self.ENV}/domain")
        if domain_data:
            self.DOMAIN = domain_data["domain"]
        else:
            print("No service domain data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/domain")

        # auth service info
        auth_data = secrets_data.get(f"{self.ENV}/auth")
        if auth_data:
            self.AUTH_TOKEN_NAME = auth_data["token_name"]
            self.AUTH_TOKEN_KEY = auth_data["token_key"]
            self.AUTH_TOKEN_EXPIRE = auth_data["expire"]
            self.AUTH_ADMIN_TMP_TOKEN = auth_data["admin_tmp_token"]
            self.AUTH_SITE_MESSAGES_TMP_TOKEN = auth_data["site_messages_tmp_token"]
        else:
            print("No auth data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/auth")

        # streamer name
        streamer_data = secrets_data.get(f"{self.ENV}/streamer")
        if streamer_data:
            self.STREAMER = streamer_data["name"]
        else:
            print("No streamer data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/streamer")

        # moderator name
        moderator_data = secrets_data.get(f"{self.ENV}/moderator")
        if moderator_data:
            self.BEST_MODERATOR = moderator_data["name"]
        else:
            print("No moderator data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/moderator")

        # twitch
        twitch_data = secrets_data.get(f"{self.ENV}/twitch")
        if twitch_data:
            self.TWITCHBOT_TOKEN = twitch_data["bot_token"]
        else:
            print("No twitch data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/twitch")

        # discord hooks
        discord_data = secrets_data.get(f"{self.ENV}/discord")
        if discord_data:
            self.DISCORD_HOOK_TIMECODE = discord_data["hook_timecode"]
            self.DISCORD_HOOK_SITE_MESSAGES = discord_data["hook_site_messages"]
        else:
            print("No discord data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/discord")

        # mal api
        mal_data = secrets_data.get(f"{self.ENV}/mal")
        if mal_data:
            self.MAL_API = mal_data["api_url"]
            self.MAL_HEADER = mal_data["header"]
            self.MAL_CLIENT_ID = mal_data["client_id"]
        else:
            print("No mal data in secrets")
            if initial:
                raise
            else:
                no_secrets.append(f"{self.ENV}/mal")

        return no_secrets


cfg = ConfigManager()
