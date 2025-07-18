from collections import deque
from typing import Deque, Iterator, List

from src.config import logger
from src.models.message import TelegramMessage, UserMessage


class SlidingWindowContext:
    """Manages a sliding window of messages to provide context for analysis.

    This class allows iterating through messages while maintaining a configurable
    window of preceding and succeeding messages, and can also follow reply chains
    to include relevant parent messages.
    """

    def __init__(
        self,
        messages: List[TelegramMessage],
        window_size: int = 5,
        reply_depth: int = 3,
        include_current_message: bool = True,
    ):
        """Initialize the SlidingWindowContext.

        Args:
            messages (List[TelegramMessage]): A list of all messages in the chat,
                                             sorted by message ID.
            window_size (int): The number of messages to include before and after
                               the current message in the context window.
            reply_depth (int): The maximum depth to follow reply chains to include
                               parent messages in the context.
            include_current_message (bool): Whether to include the current message
                                            in the returned context window.

        """
        if not all(isinstance(msg, TelegramMessage) for msg in messages):
            raise TypeError("All items in 'messages' must be instances of TelegramMessage.")
        if not all(messages[i].id < messages[i + 1].id for i in range(len(messages) - 1)):
            logger.warning("Messages are not sorted by ID. Context window might not be accurate.")

        self._messages = messages
        self._message_map = {msg.id: msg for msg in messages}  # For quick lookup by ID
        self.window_size = window_size
        self.reply_depth = reply_depth
        self.include_current_message = include_current_message

    def get_context_for_message(self, message: TelegramMessage) -> List[TelegramMessage]:
        """Retrieve the context window for a given message.

        Args:
            message (TelegramMessage): The message for which to retrieve the context.

        Returns:
            List[TelegramMessage]: A list of messages forming the context, including
                                   preceding, succeeding, and reply-chain messages,
                                   sorted by their original order.

        """
        if message.id not in self._message_map:
            logger.warning(f"Message with ID {message.id} not found in the provided message list.")
            return []

        current_message_index = -1
        for i, msg in enumerate(self._messages):
            if msg.id == message.id:
                current_message_index = i
                break

        if current_message_index == -1:
            return []  # Should not happen if message.id is in _message_map

        context_messages: Deque[TelegramMessage] = deque()

        # Add preceding messages
        for i in range(max(0, current_message_index - self.window_size), current_message_index):
            context_messages.append(self._messages[i])

        # Add current message
        if self.include_current_message:
            context_messages.append(message)

        # Add succeeding messages
        for i in range(
            current_message_index + 1, min(len(self._messages), current_message_index + 1 + self.window_size)
        ):
            context_messages.append(self._messages[i])

        # Add reply chain messages
        reply_chain_messages = self._get_reply_chain(message, self.reply_depth)
        for msg in reply_chain_messages:
            if msg not in context_messages:  # Avoid duplicates if already in window
                context_messages.appendleft(msg)  # Add to the beginning for chronological order

        # Sort the final context messages by their original ID to maintain chronological order
        # Convert deque to list for sorting
        sorted_context = sorted(list(context_messages), key=lambda msg: msg.id)

        return sorted_context

    def _get_reply_chain(self, message: TelegramMessage, depth: int) -> List[TelegramMessage]:
        """Recursively get messages in the reply chain.

        Args:
            message (TelegramMessage): The current message to check for replies.
            depth (int): The remaining depth to traverse the reply chain.

        Returns:
            List[TelegramMessage]: A list of parent messages in the reply chain.

        """
        chain = []
        if depth <= 0:
            return chain

        if isinstance(message, UserMessage) and message.reply_to_message_id:
            parent_message = self._message_map.get(message.reply_to_message_id)
            if parent_message:
                chain.append(parent_message)
                chain.extend(self._get_reply_chain(parent_message, depth - 1))
        return chain

    def iterate_with_context(self) -> Iterator[tuple[TelegramMessage, List[TelegramMessage]]]:
        """Iterate through all messages, yielding each message and its context.

        Yields:
            tuple[TelegramMessage, List[TelegramMessage]]: A tuple containing the current message
                                                           and its context window.

        """
        for message in self._messages:
            context = self.get_context_for_message(message)
            yield message, context
