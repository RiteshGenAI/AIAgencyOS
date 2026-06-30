import os

from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings


class AnthropicProvider(BaseLLM):
    def __init__(self):
        api_key = settings.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY or LLM_API_KEY is required for Anthropic provider")
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("anthropic package is not installed") from exc
        self.client = Anthropic(api_key=api_key, base_url=settings.base_url or None)
        self.default_system_prompt = "You are a helpful AI assistant."

    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        system = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system = msg.get("content", "")
            else:
                user_messages.append(msg)
        response = self.client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", settings.max_tokens),
            temperature=kwargs.get("temperature", settings.temperature),
            system=system or self.default_system_prompt,
            messages=user_messages,
        )
        return response.content[0].text.strip()

    def list_models(self) -> list[str]:
        import requests
        headers = {
            "x-api-key": self.client.api_key,
            "anthropic-version": "2023-06-01",
        }
        resp = requests.get("https://api.anthropic.com/v1/models", headers=headers, timeout=30)
        resp.raise_for_status()
        return [m["id"] for m in resp.json().get("data", [])]
