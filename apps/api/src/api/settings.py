from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    RABBITMQ_URL: str
    POSTGRES_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"


settings = Settings()  # type: ignore
