from os import getenv
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict()

    APP_MODE: Literal["api", "bot", "worker"]

    DB_NAME: str = "book_bot"
    DB_USER: str = "book_bot_user"
    DB_PASSWORD: str
    DB_PORT: str = "5432"
    DB_HOST: str = "localhost"

    REDIS_URL: str

    DEBUG: bool = True

    def get_database_url(self) -> str:
        url = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        print(url)
        return url


class ApiSettings(BaseAppSettings):
    model_config = SettingsConfigDict(
        env_file="dev-config/api.env", env_file_encoding="utf-8"
    )
    ADMIN_TG: int


class BotSettings(BaseAppSettings):
    model_config = SettingsConfigDict(
        env_file="dev-config/bot.env", env_file_encoding="utf-8"
    )
    BOT_TOKEN: str
    WEBHOOK_URL: str = ""

    PROXY_URL: str | None = None

    ADMIN_TG: int


class WorkerSettings(BaseAppSettings):
    model_config = SettingsConfigDict(
        env_file="dev-config/worker.env", env_file_encoding="utf-8"
    )
    BOT_TOKEN: str

    PROXY_URL: str | None = None


_app_mode = getenv("APP_MODE", None)

if not _app_mode:
    raise Exception("Env APP_MODE not found")

settings: ApiSettings | BotSettings | WorkerSettings

if _app_mode == "api":
    settings = ApiSettings()  # type:ignore
elif _app_mode == "bot":
    settings = BotSettings()  # type:ignore
elif _app_mode == "worker":
    settings = WorkerSettings()  # type:ignore
