from pydantic_settings import BaseSettings, SettingsConfigDict


class StrandsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STRANDS_",
        env_file=".env",
        extra="ignore",
    )

    model_provider: str = "ollama"
    model_name: str = "llama3.2"
    max_tokens: int = 4096
    temperature: float = 0.7


settings = StrandsSettings()
