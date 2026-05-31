from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    WEBHOOK_URL: str = ""
    REDIS_URL: str
    PROXY_URL: str | None = None
    RABBITMQ_URL: str
    ADMIN_TG: int
    DEBUG: bool = False

    POSTGRES_URL: str


settings = Settings()  # type: ignore
