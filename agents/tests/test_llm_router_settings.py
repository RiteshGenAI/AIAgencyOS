import importlib
import os
import unittest

from agents.app.llm_router import config


class TestLLMSettings(unittest.TestCase):
    @staticmethod
    def _settings_under_env(env):
        # Build a clean environment that strips LLM_ vars and applies the overrides.
        base = {k: v for k, v in os.environ.items() if not k.startswith("LLM_")}
        base.update(env)
        saved = dict(os.environ)
        os.environ.clear()
        os.environ.update(base)
        try:
            importlib.reload(config)
            return config.settings
        finally:
            os.environ.clear()
            os.environ.update(saved)
            importlib.reload(config)

    def test_defaults(self):
        settings = self._settings_under_env({})
        self.assertEqual(settings.provider, "ollama")
        self.assertEqual(settings.model, "llama3.2")
        self.assertIsNone(settings.base_url)
        self.assertIsNone(settings.api_key)
        self.assertEqual(settings.max_tokens, 1024)
        self.assertAlmostEqual(settings.temperature, 0.7)

    def test_env_overrides(self):
        settings = self._settings_under_env({
            "LLM_PROVIDER": "openai",
            "LLM_MODEL": "gpt-4o",
            "LLM_BASE_URL": "http://localhost:8000/v1",
            "LLM_API_KEY": "sk-test",
            "LLM_MAX_TOKENS": "2048",
            "LLM_TEMPERATURE": "0.5",
        })
        self.assertEqual(settings.provider, "openai")
        self.assertEqual(settings.model, "gpt-4o")
        self.assertEqual(settings.base_url, "http://localhost:8000/v1")
        self.assertEqual(settings.api_key, "sk-test")
        self.assertEqual(settings.max_tokens, 2048)
        self.assertAlmostEqual(settings.temperature, 0.5)

    def test_extra_env_ignored(self):
        settings = self._settings_under_env({"LLM_UNKNOWN_VAR": "ignored"})
        self.assertFalse(hasattr(settings, "unknown_var"))


if __name__ == "__main__":
    unittest.main()
