"""No real Ollama server here: urllib.request.urlopen is mocked so these
pin the HTTP-error-vs-connection-error split without any network access.
"""
import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from harness.llm_eval import OllamaProvider, ProviderError


def _http_error(code, body):
    return urllib.error.HTTPError(
        "http://localhost:11434/api/generate", code, "reason", {}, io.BytesIO(body)
    )


def test_ask_returns_the_response_field_on_success():
    ok_body = io.BytesIO(json.dumps({"response": "20\n"}).encode("utf-8"))
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = ok_body.read()
        result = OllamaProvider("llama3.1").ask("predict this")

    assert result == "20\n"


def test_ask_reports_a_model_not_found_error_distinctly_from_a_connection_error():
    with patch("urllib.request.urlopen", side_effect=_http_error(404, b"model not found")):
        with pytest.raises(ProviderError, match="rejected the request for model"):
            OllamaProvider("not-a-real-model").ask("predict this")


def test_ask_reports_a_connection_failure_distinctly_from_a_model_error():
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        with pytest.raises(ProviderError, match="Could not reach Ollama"):
            OllamaProvider("llama3.1").ask("predict this")


def test_ask_raises_on_a_response_with_no_response_field():
    bad_body = io.BytesIO(json.dumps({"unexpected": "shape"}).encode("utf-8"))
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = bad_body.read()
        with pytest.raises(ProviderError, match="Unexpected Ollama response shape"):
            OllamaProvider("llama3.1").ask("predict this")
