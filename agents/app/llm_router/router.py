from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings
from agents.app.llm_router.providers.openai_provider import OpenAIProvider
from agents.app.llm_router.providers.anthropic_provider import AnthropicProvider
from agents.app.llm_router.providers.ollama_provider import OllamaProvider


_PROVIDER_MAP: dict[str, type[BaseLLM]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


def get_llm(provider: str | None = None) -> BaseLLM:
    provider = (provider or settings.provider).lower()
    if provider not in _PROVIDER_MAP:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return _PROVIDER_MAP[provider]()


def generate(model: str | None = None, messages: list[dict] | None = None, **kwargs) -> str:
    llm = get_llm()
    return llm.generate(
        model=model or settings.model,
        messages=messages or [],
        **kwargs,
    )
