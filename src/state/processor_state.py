import json
from pathlib import Path
from typing import Dict, Optional, Union

from pydantic import BaseModel, Field, ValidationError

from src.config import logger


class ProcessingState(BaseModel):
    """Represents the state of the chat analysis processing.

    This model tracks the progress of the analysis, including the last processed message ID,
    and can be saved to/loaded from a JSON file to enable resumable processing.
    """

    chat_export_path: Path = Field(..., description="The path to the Telegram chat export file being processed.")
    last_processed_message_id: int = Field(0, description="The ID of the last message successfully processed.", ge=0)
    total_messages_processed: int = Field(0, description="The total count of messages processed so far.", ge=0)
    start_time: Optional[str] = Field(None, description="Timestamp when the processing started (ISO 8601 format).")
    end_time: Optional[str] = Field(None, description="Timestamp when the processing ended (ISO 8601 format).")
    status: str = Field(
        "pending",
        description="Current status of the processing (e.g., 'pending', 'in_progress', 'completed', 'failed').",
    )
    # Add more fields as needed, e.g., for accumulated facts, errors, etc.
    # For now, we'll keep it simple and focus on message processing progress.
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="A dictionary for storing arbitrary processing metadata."
    )

    def save(self, state_file_path: Union[str, Path]) -> None:
        """Save the current state to a JSON file.

        Args:
            state_file_path (Union[str, Path]): The path to the file where the state will be saved.

        """
        path = Path(state_file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.model_dump_json(indent=4))
            logger.info(f"Processing state saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save processing state to {path}: {e}")
            raise

    @classmethod
    def load(cls, state_file_path: Union[str, Path]) -> Optional["ProcessingState"]:
        """Load the processing state from a JSON file.

        Args:
            state_file_path (Union[str, Path]): The path to the state file.

        Returns:
            Optional[ProcessingState]: The loaded ProcessingState object, or None if the file
                                      does not exist or is invalid.

        """
        path = Path(state_file_path)
        if not path.exists():
            logger.info(f"No existing state file found at {path}.")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state = cls.model_validate(data)
            logger.info(
                f"Processing state loaded from {path}. Last processed message ID: {state.last_processed_message_id}"
            )
            return state
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to load or validate processing state from {path}: {e}")
            # Optionally, you might want to delete the corrupted file here
            # path.unlink(missing_ok=True)
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading state from {path}: {e}")
            return None

    def reset(self) -> None:
        """Reset the processing state to its initial values."""
        self.last_processed_message_id = 0
        self.total_messages_processed = 0
        self.start_time = None
        self.end_time = None
        self.status = "pending"
        self.metadata = {}
        logger.info("Processing state reset.")
