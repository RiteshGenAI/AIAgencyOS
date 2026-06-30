import unittest
from unittest.mock import patch

from agents.app.llm_router import config, get_llm, generate
from agents.app.llm_router.providers.ollama_provider import OllamaProvider


class TestLLMRouterFactory(unittest.TestCase):
    def test_get_llm_defaults_to_ollama(self):
        with patch.object(config.settings, "provider", "ollama"):
            llm = get_llm()
            self.assertIsInstance(llm, OllamaProvider)

    def test_get_llm_explicit_provider(self):
        llm = get_llm("ollama")
        self.assertIsInstance(llm, OllamaProvider)

    def test_get_llm_unsupported_raises(self):
        with self.assertRaises(ValueError) as ctx:
            get_llm("unknown")
        self.assertIn("Unsupported LLM provider", str(ctx.exception))

    @patch.object(OllamaProvider, "generate", return_value="hello")
    def test_generate_uses_default_settings(self, mock_generate):
        with patch.object(config.settings, "provider", "ollama"):
            with patch.object(config.settings, "model", "llama3.2"):
                result = generate(messages=[{"role": "user", "content": "hi"}])
                self.assertEqual(result, "hello")
                mock_generate.assert_called_once_with(
                    model="llama3.2",
                    messages=[{"role": "user", "content": "hi"}],
                )


if __name__ == "__main__":
    unittest.main()
