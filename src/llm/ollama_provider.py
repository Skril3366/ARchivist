import json
from typing import Any, Dict, List, Optional

import requests

from src.config import OLLAMA_API_BASE_URL, logger
from src.llm.llm_interface import LLMProvider


class OllamaProvider(LLMProvider):
    """Concrete implementation of LLMProvider for Ollama.

    Handles communication with a local Ollama instance.
    """

    def __init__(self, model_name: str = "gemma3n:latest", api_base_url: Optional[str] = None, **kwargs):
        """Initialize the OllamaProvider.

        Args:
            model_name (str): The name of the Ollama model to use (e.g., "gemma3n:latest").
            api_base_url (Optional[str]): The base URL for the Ollama API.
                                          Defaults to OLLAMA_API_BASE_URL from config.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(model_name, api_base_url or OLLAMA_API_BASE_URL)
        self.timeout = kwargs.get("timeout", 120)  # Default timeout of 120 seconds
        self._session = requests.Session()  # Use a session for connection pooling

    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make requests to the Ollama API.

        This is a helper method to handle common request logic, error handling, and JSON parsing.
        """
        url = f"{self.api_base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self._session.get(url, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self._session.post(url, json=payload, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Ollama API request timed out after {self.timeout} seconds for {endpoint}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to Ollama at {self.api_base_url}. Is it running?")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama API HTTP error for {endpoint}: {e.response.status_code} - {e.response.text}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON response from Ollama for {endpoint}: {response.text}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during Ollama API request to {endpoint}: {e}")
            raise

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the Ollama /generate endpoint.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional parameters for generation (e.g., `options` dict for temperature, top_k).

        Returns:
            str: The generated text.

        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,  # We want the full response at once
            "options": kwargs.get("options", {}),
        }
        logger.debug(f"Sending generate request to Ollama for model {self.model_name}")
        response_data = self._make_request("POST", "/api/generate", payload)
        return response_data.get("response", "").strip()

    def generate_structured_output(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured output (JSON) using the Ollama /generate endpoint with format.

        Args:
            prompt (str): The input prompt.
            schema (Dict[str, Any]): The JSON schema defining the desired output structure.
            **kwargs: Additional parameters for generation.

        Returns:
            Dict[str, Any]: The generated structured output as a dictionary.

        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "format": "json",  # Request JSON output
            "stream": False,
            "options": kwargs.get("options", {}),
        }
        logger.debug(f"Sending structured generate request to Ollama for model {self.model_name}")
        response_data = self._make_request("POST", "/api/generate", payload)
        try:
            # Ollama returns the JSON string within the "response" field
            json_string = response_data.get("response", "")
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Ollama structured output: {e}. Response: {response_data}")
            raise ValueError(f"Invalid JSON response from LLM: {e}") from e

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat completion using the Ollama /chat endpoint.

        Args:
            messages (List[Dict[str, str]]): A list of message dictionaries,
                                              e.g., [{"role": "user", "content": "Hello!"}].
            **kwargs: Additional parameters for chat completion.

        Returns:
            str: The generated response from the AI.

        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": kwargs.get("options", {}),
        }
        logger.debug(f"Sending chat completion request to Ollama for model {self.model_name}")
        response_data = self._make_request("POST", "/api/chat", payload)
        return response_data.get("message", {}).get("content", "").strip()

    def is_available(self) -> bool:
        """Check if the Ollama service is available and the model is loaded.

        Returns:
            bool: True if the service is available and model exists, False otherwise.

        """
        try:
            # Check if the model exists locally by making a GET request to /api/tags
            model_tags = self._make_request("GET", "/api/tags")
            logger.info(f"Ollama service is reachable at {self.api_base_url}")
            available_models = [m["name"] for m in model_tags.get("models", [])]
            if self.model_name in available_models:
                logger.info(f"Model '{self.model_name}' is already available.")
                return True

            logger.warning(f"Model '{self.model_name}' not found locally. Attempting to pull...")
            # Attempt to pull the model, handling the streaming response
            pull_url = f"{self.api_base_url}/api/pull"
            pull_payload = {"name": self.model_name, "stream": True}  # Request streaming
            pull_success = False
            try:
                with self._session.post(pull_url, json=pull_payload, stream=True, timeout=self.timeout) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            try:
                                json_response = json.loads(line)
                                if json_response.get("status") == "success":
                                    pull_success = True
                                    logger.info(f"Successfully pulled model '{self.model_name}'.")
                                elif json_response.get("error"):
                                    logger.error(
                                        f"Error pulling model '{self.model_name}': {json_response.get('error')}"
                                    )
                                    pull_success = False
                                    break  # Exit loop on error
                                else:
                                    logger.debug(f"Pull progress for {self.model_name}: {json_response.get('status')}")
                            except json.JSONDecodeError:
                                logger.warning(f"Received non-JSON line during pull: {line}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error during model pull for '{self.model_name}': {e}")
                pull_success = False

            return pull_success
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
            logger.error(f"Ollama service or model check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during Ollama availability check: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded Ollama model.

        Returns:
            Dict[str, Any]: A dictionary containing model details.

        """
        try:
            # Ollama doesn't have a direct "get model info" endpoint for a specific model
            # without running it. We can list all models and find ours.
            model_tags = self._make_request("GET", "/api/tags")
            for model in model_tags.get("models", []):
                if model.get("name") == self.model_name:
                    return model
            logger.warning(f"Model '{self.model_name}' not found in Ollama's list of models.")
            return {}
        except Exception as e:
            logger.error(f"Failed to get model info for '{self.model_name}': {e}")
            return {}
