from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://nomadia:nomadia@localhost:5432/nomadia_api"
    strapi_url: str = "http://localhost:1337"
    strapi_token: str = ""
    cors_origins: str = "http://localhost:4321"


@lru_cache
def get_settings() -> Settings:
    return Settings()
