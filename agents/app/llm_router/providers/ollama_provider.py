import json
import os

import requests

from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings


class OllamaProvider(BaseLLM):
    def __init__(self):
        self.base_url = (settings.base_url or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")

    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        prompt = "\n".join(
            f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages
        )
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", settings.temperature),
                "num_predict": kwargs.get("max_tokens", settings.max_tokens),
            },
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        parts = []
        for line in response.text.strip().splitlines():
            if line:
                try:
                    data = json.loads(line)
                    parts.append(data.get("response", ""))
                except json.JSONDecodeError:
                    continue
        return "".join(parts).strip()

    def list_models(self) -> list[str]:
        response = requests.get(f"{self.base_url}/api/tags", timeout=30)
        response.raise_for_status()
        return [m.get("name", m.get("model", "unknown")) for m in response.json().get("models", [])]
