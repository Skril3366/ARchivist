from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

from src.models.enums import ActionType, EntityType, MessageType


class TextEntity(BaseModel):
    """Represents a text entity within a message, such as bold, italic, or a URL."""

    type: EntityType
    text: str
    href: Optional[str] = None  # For URL entities
    # Add other fields like `user_id` for mentions if needed


class TelegramMessage(BaseModel):
    """Base model for a Telegram message, covering common fields."""

    id: int
    type: MessageType
    date: datetime
    date_unixtime: str = Field(..., pattern=r"^\d+$")  # Unix timestamp as string, e.g., "1688192400"

    # Optional fields common to both message and service types
    from_name: Optional[str] = Field(None, alias="from")  # Renamed to avoid Python keyword conflict
    from_id: Optional[str] = None  # e.g., "user12345678" or "channel12345"
    edited: Optional[datetime] = None
    edited_unixtime: Optional[str] = Field(None, pattern=r"^\d+$")

    @field_validator("date", "edited", mode="before")
    @classmethod
    def parse_datetime_string(cls, value: str) -> datetime:
        """Parse a datetime string into a datetime object."""
        return datetime.fromisoformat(value)


class UserMessage(TelegramMessage):
    """Represents a standard user message."""

    type: Literal[MessageType.MESSAGE] = MessageType.MESSAGE
    text: Union[str, List[Union[str, TextEntity]]]
    reply_to_message_id: Optional[int] = None
    forwarded_from: Optional[str] = None
    forwarded_from_id: Optional[str] = None
    file: Optional[str] = None  # Relative path to file attachment
    mime_type: Optional[str] = None  # MIME type of attached file
    photo: Optional[str] = None  # Relative path to photo media file
    width: Optional[int] = None  # Dimensions of attached photo
    height: Optional[int] = None  # Dimensions of attached photo
    # text_entities is implicitly handled by the Union[str, List[Union[str, TextEntity]]] for 'text'
    # If 'text' is a list, it contains TextEntity objects.


class ServiceMessage(TelegramMessage):
    """Represents a service message (e.g., user joined, title changed)."""

    type: Literal[MessageType.SERVICE] = MessageType.SERVICE
    actor: Optional[str] = None  # Display name of the user who performed the action
    actor_id: Optional[str] = None  # ID of the actor (e.g., "user12345678")
    action: ActionType
    members: Optional[List[str]] = None  # Affected users for member-related actions


class Chat(BaseModel):
    """Represents the top-level structure of a Telegram chat export."""

    name: str
    type: str  # e.g., "personal_chat", "private_group", "channel"
    id: int
    messages: List[Union[UserMessage, ServiceMessage]] = Field(default_factory=list)

    @field_validator("messages", mode="before")
    @classmethod
    def parse_messages(cls, messages_data: List[dict]) -> List[Union[UserMessage, ServiceMessage]]:
        """Parse raw message dictionaries into UserMessage or ServiceMessage models."""
        parsed_messages = []
        for msg_data in messages_data:
            msg_type = msg_data.get("type")
            if msg_type == MessageType.MESSAGE.value:
                parsed_messages.append(UserMessage.model_validate(msg_data))
            elif msg_type == MessageType.SERVICE.value:
                parsed_messages.append(ServiceMessage.model_validate(msg_data))
            else:
                # Log a warning or raise an error for unknown message types
                # For now, we'll just skip it or let Pydantic handle validation errors
                pass
        return parsed_messages
