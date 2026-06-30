import importlib
import os
import unittest

from agents.app.strands.core import config
from agents.app.strands.core import strands_config


class TestStrandsSettings(unittest.TestCase):
    @staticmethod
    def _reload_both(env):
        base = {k: v for k, v in os.environ.items() if not k.startswith("STRANDS_")}
        base.update(env)
        saved = dict(os.environ)
        os.environ.clear()
        os.environ.update(base)
        try:
            importlib.reload(config)
            importlib.reload(strands_config)
            return config.settings, strands_config.settings
        finally:
            os.environ.clear()
            os.environ.update(saved)
            importlib.reload(config)
            importlib.reload(strands_config)

    def test_config_defaults(self):
        core, sdk = self._reload_both({})
        self.assertEqual(core.model_name, "anthropic.claude-3-5-sonnet")
        self.assertEqual(core.max_tokens, 4096)
        self.assertAlmostEqual(core.temperature, 0.7)
        self.assertEqual(core.sentinel_base_url, "http://backend:8000/internal/sentinel")
        self.assertIsNone(core.agentcore_endpoint)

    def test_strands_config_defaults(self):
        core, sdk = self._reload_both({})
        self.assertEqual(sdk.model_provider, "ollama")
        self.assertEqual(sdk.model_name, "llama3.2")
        self.assertEqual(sdk.max_tokens, 4096)

    def test_env_prefix_override(self):
        core, sdk = self._reload_both({
            "STRANDS_MODEL_NAME": "custom-model",
            "STRANDS_MAX_TOKENS": "512",
            "STRANDS_SENTINEL_BASE_URL": "http://test/sentinel",
            "STRANDS_MODEL_PROVIDER": "openai",
        })
        self.assertEqual(core.model_name, "custom-model")
        self.assertEqual(core.max_tokens, 512)
        self.assertEqual(core.sentinel_base_url, "http://test/sentinel")
        self.assertEqual(sdk.model_provider, "openai")


if __name__ == "__main__":
    unittest.main()
