from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.development", env_file_encoding="utf-8"
    )

    DB_NAME: str = "book_bot"
    DB_USER: str = "book_bot_user"
    DB_PASSWORD: str
    DB_PORT: str = "5432"
    DB_HOST: str = "localhost"

    REDIS_URL: str

    BOT_TOKEN: str
    WEBHOOK_URL: str = ""
    DEBUG: bool = True

    PROXY_URL: str | None = None

    ADMIN_TG: int

    def get_database_url(self) -> str:
        url = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        print(url)
        return url


settings = Settings()


if __name__ == "__main__":
    print(settings.DB_NAME)
    print(settings.DB_PORT)
    print(settings.DB_USER)
    print(settings.DB_PASSWORD)
