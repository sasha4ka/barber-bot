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

    DB_NAME: str = "book_bot"
    DB_USER: str = "book_bot_user"
    DB_PASSWORD: str
    DB_PORT: str = "5432"
    DB_HOST: str = "localhost"

    def get_database_url(self) -> str:
        url = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        print(url)
        return url


settings = Settings()  # type: ignore
