from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        """Return the model's text response for the given messages."""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return available model IDs."""
        pass
