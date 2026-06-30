from pydantic_settings import BaseSettings, SettingsConfigDict


class StrandsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STRANDS_",
        env_file=".env",
        extra="ignore",
    )

    model_name: str = "anthropic.claude-3-5-sonnet"
    max_tokens: int = 4096
    temperature: float = 0.7

    sentinel_base_url: str = "http://backend:8000/internal/sentinel"
    agentcore_endpoint: str | None = None


settings = StrandsSettings()
