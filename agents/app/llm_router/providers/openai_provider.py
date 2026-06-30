import os

from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings


class OpenAIProvider(BaseLLM):
    def __init__(self):
        api_key = settings.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY or LLM_API_KEY is required for OpenAI provider")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed") from exc
        self.client = OpenAI(api_key=api_key, base_url=settings.base_url or None)

    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", settings.max_tokens),
            temperature=kwargs.get("temperature", settings.temperature),
        )
        return response.choices[0].message.content.strip()

    def list_models(self) -> list[str]:
        models = self.client.models.list()
        return sorted([m.id for m in models.data])
