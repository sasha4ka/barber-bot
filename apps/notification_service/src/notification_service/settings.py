from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    BOT_TOKEN: str
    RABBITMQ_URL: str
    PROXY_URL: str | None = None


settings: Settings = Settings()  # type: ignore
