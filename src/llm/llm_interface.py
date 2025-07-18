from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMProvider(ABC):
    """Abstract base class for Large Language Model (LLM) providers.

    Defines the common interface for interacting with different LLMs.
    """

    @abstractmethod
    def __init__(self, model_name: str, api_base_url: Optional[str] = None, **kwargs):
        """Initialize the LLM provider.

        Args:
            model_name (str): The name of the LLM model to use (e.g., "gemma:2b").
            api_base_url (Optional[str]): The base URL for the LLM API.
            **kwargs: Additional keyword arguments specific to the provider.

        """
        self.model_name = model_name
        self.api_base_url = api_base_url

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text based on a given prompt.

        Args:
            prompt (str): The input prompt for text generation.
            **kwargs: Additional keyword arguments for text generation (e.g., temperature, max_tokens).

        Returns:
            str: The generated text.

        """
        pass

    @abstractmethod
    def generate_structured_output(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured output (e.g., JSON) based on a prompt and a schema.

        Args:
            prompt (str): The input prompt.
            schema (Dict[str, Any]): The JSON schema defining the desired output structure.
            **kwargs: Additional keyword arguments for generation.

        Returns:
            Dict[str, Any]: The generated structured output as a dictionary.

        """
        pass

    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat completion based on a list of messages.

        Args:
            messages (List[Dict[str, str]]): A list of message dictionaries,
                                              e.g., [{"role": "user", "content": "Hello!"}].
            **kwargs: Additional keyword arguments for chat completion.

        Returns:
            str: The generated response from the AI.

        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available and reachable.

        Returns:
            bool: True if the service is available, False otherwise.

        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.

        Returns:
            Dict[str, Any]: A dictionary containing model details.

        """
        pass
