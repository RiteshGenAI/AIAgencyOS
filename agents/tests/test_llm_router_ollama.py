import json
import unittest
from unittest.mock import patch, MagicMock

from agents.app.llm_router.providers.ollama_provider import OllamaProvider


class TestOllamaProvider(unittest.TestCase):
    def setUp(self):
        self.provider = OllamaProvider()

    @patch("agents.app.llm_router.providers.ollama_provider.requests.post")
    def test_generate_single_json_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.text = json.dumps({"response": " generated copy "})
        mock_post.return_value = mock_response

        result = self.provider.generate(
            model="llama3.2",
            messages=[{"role": "user", "content": "write copy"}],
        )
        self.assertEqual(result, "generated copy")
        mock_response.raise_for_status.assert_called_once()

    @patch("agents.app.llm_router.providers.ollama_provider.requests.post")
    def test_generate_ndjson_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.text = "\n".join([
            json.dumps({"response": "line1"}),
            json.dumps({"response": " line2 "}),
            "not-json",
        ])
        mock_post.return_value = mock_response

        result = self.provider.generate(
            model="llama3.2",
            messages=[{"role": "user", "content": "write copy"}],
        )
        self.assertEqual(result, "line1 line2")

    @patch("agents.app.llm_router.providers.ollama_provider.requests.get")
    def test_list_models(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2", "model": "ignored"},
                {"model": "mistral"},
            ]
        }
        mock_get.return_value = mock_response

        models = self.provider.list_models()
        self.assertEqual(models, ["llama3.2", "mistral"])


if __name__ == "__main__":
    unittest.main()
