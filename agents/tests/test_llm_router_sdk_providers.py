import os
import unittest

from agents.app.llm_router.providers.openai_provider import OpenAIProvider
from agents.app.llm_router.providers.anthropic_provider import AnthropicProvider


class TestSDKProvidersInit(unittest.TestCase):
    def test_openai_requires_api_key(self):
        env = os.environ.copy()
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("LLM_API_KEY", None)
        try:
            with self.assertRaises(RuntimeError) as ctx:
                OpenAIProvider()
            self.assertIn("OPENAI_API_KEY or LLM_API_KEY", str(ctx.exception))
        finally:
            os.environ.update(env)

    def test_openai_requires_package(self):
        # Provide a key but rely on openai package being absent in this env.
        with unittest.mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with unittest.mock.patch("builtins.__import__", side_effect=ImportError("no openai")):
                with self.assertRaises(RuntimeError) as ctx:
                    OpenAIProvider()
                self.assertIn("openai package is not installed", str(ctx.exception))

    def test_anthropic_requires_api_key(self):
        env = os.environ.copy()
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("LLM_API_KEY", None)
        try:
            with self.assertRaises(RuntimeError) as ctx:
                AnthropicProvider()
            self.assertIn("ANTHROPIC_API_KEY or LLM_API_KEY", str(ctx.exception))
        finally:
            os.environ.update(env)


if __name__ == "__main__":
    unittest.main()
