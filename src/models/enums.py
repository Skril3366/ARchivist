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
    LINK = "link"
    TEXT_LINK = "text_link"
    BLOCKQUOTE = "blockquote"  # Added from provided data
    MENTION_NAME = "mention_name"  # Added from provided data


class ActionType(str, Enum):
    """Enum for different types of service message actions."""

    INVITE_MEMBERS = "invite_members"
    PHOTO_CHANGED = "photo_changed"
    TITLE_CHANGED = "title_changed"
    LEFT_GROUP = "left_group"
    PIN_MESSAGE = "pin_message"
    CREATE_GROUP = "create_group"
    CREATE_CHANNEL = "create_channel"
    EDIT_MESSAGE = "edit_message"
    DELETE_MESSAGE = "delete_message"
    MIGRATE_FROM_GROUP = "migrate_from_group"
    TOPIC_CREATED = "topic_created"
    JOIN_GROUP_BY_LINK = "join_group_by_link"
    BOOST_APPLY = "boost_apply"  # Added from provided data
    EDIT_GROUP_PHOTO = "edit_group_photo"  # Added from provided data
    EDIT_GROUP_TITLE = "edit_group_title"  # Added from provided data
    GROUP_CALL = "group_call"  # Added from provided data
    REMOVE_MEMBERS = "remove_members"  # Added from provided data
