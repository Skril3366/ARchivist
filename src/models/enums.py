from enum import Enum


class MessageType(str, Enum):
    """Enum for different types of Telegram messages."""

    MESSAGE = "message"
    SERVICE = "service"


class EntityType(str, Enum):
    """Enum for different types of text entities within a message."""

    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    PRE = "pre"
    URL = "url"
    MENTION = "mention"
    HASHTAG = "hashtag"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SPOILER = "spoiler"
    CUSTOM_EMOJI = "custom_emoji"
    PHONE = "phone"
    EMAIL = "email"
    CASHTAG = "cashtag"
    BOT_COMMAND = "bot_command"


class ActionType(str, Enum):
    """Enum for different types of service message actions."""

    INVITE_MEMBERS = "invite_members"
    PHOTO_CHANGED = "photo_changed"
    TITLE_CHANGED = "title_changed"
    LEFT_GROUP = "left_group"
    PIN_MESSAGE = "pin_message"
    CREATE_GROUP = "create_group"
    CREATE_CHANNEL = "create_channel"
    EDIT_MESSAGE = "edit_message"  # Not explicitly in TELEGRAM_MESSAGE_STRUCTURE.md but common
    DELETE_MESSAGE = "delete_message"  # Not explicitly in TELEGRAM_MESSAGE_STRUCTURE.md but common
    # Add other service actions as discovered
