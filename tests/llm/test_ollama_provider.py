import json
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.llm.ollama_provider import OllamaProvider


# Fixture to create an OllamaProvider instance
@pytest.fixture(scope="module")
def ollama_provider():
    # Use a test-specific model name if desired, or rely on default
    provider = OllamaProvider(model_name="gemma3n:latest")
    return provider


# Test basic initialization
def test_ollama_provider_init(ollama_provider):
    assert ollama_provider.model_name == "gemma3n:latest"
    assert ollama_provider.api_base_url == os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")
    assert ollama_provider.timeout == 120


# Test is_available method (requires running Ollama instance)
@pytest.mark.integration
def test_ollama_provider_is_available_and_pulls_model(ollama_provider):
    # This test will attempt to connect to Ollama and pull the model if it's not there.
    # It might take a while on the first run.
    try:
        assert ollama_provider.is_available() is True
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama instance not running or not reachable.")


# Test generate_text method (requires running Ollama instance)
@pytest.mark.integration
def test_ollama_provider_generate_text(ollama_provider):
    try:
        prompt = "Tell me a short story about a brave knight."
        response = ollama_provider.generate_text(prompt)
        assert isinstance(response, str)
        assert len(response) > 50  # Expect a reasonably long story
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama instance not running or not reachable.")
    except Exception as e:
        pytest.fail(f"Text generation failed: {e}")


# Test generate_structured_output method (requires running Ollama instance)
@pytest.mark.integration
def test_ollama_provider_generate_structured_output(ollama_provider):
    try:
        prompt = "Extract the name and age from 'My name is Alice and I am 30 years old.'"
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
        response = ollama_provider.generate_structured_output(prompt, schema)

        assert isinstance(response, dict)
        assert "name" in response
        assert "age" in response
        assert response["name"].lower() == "alice"
        assert response["age"] == 30
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama instance not running or not reachable.")
    except Exception as e:
        pytest.fail(f"Structured output generation failed: {e}")


# Test chat_completion method (requires running Ollama instance)
@pytest.mark.integration
def test_ollama_provider_chat_completion(ollama_provider):
    try:
        messages = [
            {"role": "user", "content": "What is the capital of France?"},
        ]
        response = ollama_provider.chat_completion(messages)
        assert isinstance(response, str)
        assert "paris" in response.lower()
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama instance not running or not reachable.")
    except Exception as e:
        pytest.fail(f"Chat completion failed: {e}")


# Test _make_request for connection error
def test_make_request_connection_error(ollama_provider):
    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError
        with pytest.raises(requests.exceptions.ConnectionError):
            ollama_provider._make_request("POST", "/api/generate", {"model": "test", "prompt": "test"})


# Test _make_request for HTTP error
def test_make_request_http_error(ollama_provider):
    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error", response=mock_response
        )
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response
        with pytest.raises(requests.exceptions.HTTPError):
            ollama_provider._make_request("POST", "/api/generate", {"model": "test", "prompt": "test"})


# Test _make_request for JSON decode error
def test_make_request_json_decode_error(ollama_provider):
    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", doc="{}", pos=0)
        mock_post.return_value = mock_response
        with pytest.raises(json.JSONDecodeError):
            ollama_provider._make_request("POST", "/api/generate", {"model": "test", "prompt": "test"})


# Test get_model_info
def test_get_model_info(ollama_provider):
    with patch.object(ollama_provider, "_make_request") as mock_make_request:
        mock_make_request.return_value = {
            "models": [
                {"name": "gemma3n:latest", "size": 12345, "digest": "abc"},
                {"name": "llama2:7b", "size": 67890, "digest": "def"},
            ]
        }
        info = ollama_provider.get_model_info()
        assert info == {"name": "gemma3n:latest", "size": 12345, "digest": "abc"}
        mock_make_request.assert_called_once_with("GET", "/api/tags")


def test_get_model_info_model_not_found(ollama_provider):
    with patch.object(ollama_provider, "_make_request") as mock_make_request:
        mock_make_request.return_value = {
            "models": [
                {"name": "llama2:7b", "size": 67890, "digest": "def"},
            ]
        }
        info = ollama_provider.get_model_info()
        assert info == {}
        mock_make_request.assert_called_once_with("GET", "/api/tags")


# Test is_available when model needs to be pulled
def test_is_available_pulls_model(ollama_provider):
    with (
        patch.object(ollama_provider, "_make_request") as mock_make_request,
        patch("requests.Session.post") as mock_session_post,
    ):  # Mock Session.post for streaming pull
        # Simulate model not being found initially via _make_request for /api/tags
        mock_make_request.return_value = {"models": []}

        # Simulate streaming pull response
        mock_response_stream = MagicMock()
        mock_response_stream.iter_lines.return_value = [b'{"status": "downloading"}', b'{"status": "success"}']
        mock_session_post.return_value.__enter__.return_value = mock_response_stream

        assert ollama_provider.is_available() is True
        # _make_request should be called once for /api/tags
        mock_make_request.assert_called_once_with("GET", "/api/tags")
        # requests.Session.post should be called once for /api/pull
        mock_session_post.assert_called_once_with(
            f"{ollama_provider.api_base_url}/api/pull",
            json={"name": ollama_provider.model_name, "stream": True},
            stream=True,
            timeout=ollama_provider.timeout,
        )


# Test is_available when model pull fails
def test_is_available_pull_fails(ollama_provider):
    with (
        patch.object(ollama_provider, "_make_request") as mock_make_request,
        patch("requests.Session.post") as mock_session_post,
    ):  # Mock Session.post for streaming pull
        # Simulate model not being found initially via _make_request for /api/tags
        mock_make_request.return_value = {"models": []}

        # Simulate streaming pull response with an error
        mock_response_stream = MagicMock()
        mock_response_stream.iter_lines.return_value = [
            b'{"status": "downloading"}',
            b'{"status": "error", "error": "pull failed"}',
        ]
        mock_session_post.return_value.__enter__.return_value = mock_response_stream

        assert ollama_provider.is_available() is False
        # _make_request should be called once for /api/tags
        mock_make_request.assert_called_once_with("GET", "/api/tags")
        # requests.Session.post should be called once for /api/pull
        mock_session_post.assert_called_once_with(
            f"{ollama_provider.api_base_url}/api/pull",
            json={"name": ollama_provider.model_name, "stream": True},
            stream=True,
            timeout=ollama_provider.timeout,
        )
