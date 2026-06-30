from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    provider: str = "ollama"
    model: str = "llama3.2"
    base_url: str | None = None
    api_key: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.7


settings = LLMSettings()
