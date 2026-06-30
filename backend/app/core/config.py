from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BACKEND_", extra="ignore")

    SECRET_KEY: str = "change-me-secret"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Agency OS Backend"

    ENV: str = "local"  # local | cloud

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/agency_os"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    AGENTS_SERVICE_URL: str = "http://agents:8081"
    SENTINEL_URL: str = "http://sentinel:8082"
    SENTINEL_PROXY_ENABLED: bool = False

    CORS_ORIGINS: str = "http://localhost:5173"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return init_settings, env_settings, file_secret_settings, dotenv_settings

    @model_validator(mode="after")
    def check_secret_key(self):
        weak_keys = {"change-me-secret", "change-me", "secret", "dev"}
        if self.ENV == "cloud" and self.SECRET_KEY in weak_keys:
            raise RuntimeError("BACKEND_SECRET_KEY must be changed for cloud deployments.")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
