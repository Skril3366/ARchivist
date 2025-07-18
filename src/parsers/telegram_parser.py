import json
from pathlib import Path
from typing import Iterator, Union

from pydantic import ValidationError

from src.config import logger
from src.models.message import Chat, ServiceMessage, UserMessage


class TelegramChatParser:
    """A parser for Telegram chat export JSON files.

    This class handles loading, validating, and iterating through messages
    from a Telegram chat export JSON file, converting them into Pydantic models.
    """

    def __init__(self, chat_export_path: Union[str, Path]):
        """Initialize the parser with the path to the chat export file.

        Args:
            chat_export_path (Union[str, Path]): The path to the Telegram chat export JSON file.

        """
        self.chat_export_path = Path(chat_export_path)
        self._chat_data: Chat = None

    def load_and_validate(self) -> Chat:
        """Load and validate the Telegram chat export JSON file.

        Raises:
            FileNotFoundError: If the chat export file does not exist.
            json.JSONDecodeError: If the file is not a valid JSON.
            ValidationError: If the JSON structure does not conform to the Chat model.

        Returns:
            Chat: A Pydantic Chat model representing the loaded chat data.

        """
        if not self.chat_export_path.exists():
            logger.error(f"Chat export file not found: {self.chat_export_path}")
            raise FileNotFoundError(f"Chat export file not found: {self.chat_export_path}")

        logger.info(f"Loading chat export from: {self.chat_export_path}")
        try:
            with open(self.chat_export_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            self._chat_data = Chat.model_validate(raw_data)
            logger.info(f"Successfully loaded and validated chat: {self._chat_data.name}")
            return self._chat_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {self.chat_export_path}: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Chat data validation failed for {self.chat_export_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading chat data: {e}")
            raise

    def get_messages(self) -> Iterator[Union[UserMessage, ServiceMessage]]:
        """Get an iterator for messages in the chat.

        Loads the chat data if not already loaded.

        Yields:
            Union[UserMessage, ServiceMessage]: A message object from the chat.

        """
        if self._chat_data is None:
            self.load_and_validate()

        logger.info(f"Iterating through {len(self._chat_data.messages)} messages.")
        for message in self._chat_data.messages:
            yield message

    @property
    def chat_name(self) -> str:
        """Return the name of the chat."""
        if self._chat_data is None:
            self.load_and_validate()
        return self._chat_data.name

    @property
    def total_messages(self) -> int:
        """Return the total number of messages in the chat."""
        if self._chat_data is None:
            self.load_and_validate()
        return len(self._chat_data.messages)
