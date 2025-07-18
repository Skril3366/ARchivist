import logging
from datetime import datetime
from typing import List

import pytest
from loguru import logger as loguru_logger

from src.models.enums import MessageType
from src.models.message import TelegramMessage, UserMessage
from src.processing.context_manager import SlidingWindowContext


# Helper function to create dummy messages
def create_dummy_messages(count: int) -> List[TelegramMessage]:
    messages = []
    for i in range(1, count + 1):
        messages.append(
            UserMessage(
                id=i,
                type=MessageType.MESSAGE,
                date=datetime.now().isoformat(),
                date_unixtime=str(int(datetime.now().timestamp())),
                from_name=f"User{i}",
                from_id=f"user_id_{i}",
                text=f"Message {i}",
            )
        )
    return messages


def test_sliding_window_context_initialization():
    messages = create_dummy_messages(10)
    context_manager = SlidingWindowContext(messages, window_size=3, reply_depth=2)

    assert context_manager.window_size == 3
    assert context_manager.reply_depth == 2
    assert context_manager.include_current_message is True
    assert len(context_manager._messages) == 10
    assert len(context_manager._message_map) == 10


def test_get_context_for_message_middle():
    messages = create_dummy_messages(10)
    context_manager = SlidingWindowContext(messages, window_size=2, reply_depth=0)

    # Test message 5 (index 4)
    target_message = messages[4]  # Message ID 5
    context = context_manager.get_context_for_message(target_message)

    # Expected: messages 3, 4, 5, 6, 7 (IDs)
    expected_ids = [3, 4, 5, 6, 7]
    assert [msg.id for msg in context] == expected_ids
    assert len(context) == 5


def test_get_context_for_message_beginning():
    messages = create_dummy_messages(10)
    context_manager = SlidingWindowContext(messages, window_size=3, reply_depth=0)

    # Test message 1 (index 0)
    target_message = messages[0]  # Message ID 1
    context = context_manager.get_context_for_message(target_message)

    # Expected: messages 1, 2, 3, 4 (IDs)
    expected_ids = [1, 2, 3, 4]
    assert [msg.id for msg in context] == expected_ids
    assert len(context) == 4


def test_get_context_for_message_end():
    messages = create_dummy_messages(10)
    context_manager = SlidingWindowContext(messages, window_size=3, reply_depth=0)

    # Test message 10 (index 9)
    target_message = messages[9]  # Message ID 10
    context = context_manager.get_context_for_message(target_message)

    # Expected: messages 7, 8, 9, 10 (IDs)
    expected_ids = [7, 8, 9, 10]
    assert [msg.id for msg in context] == expected_ids
    assert len(context) == 4


def test_get_context_for_message_no_current_message():
    messages = create_dummy_messages(10)
    context_manager = SlidingWindowContext(messages, window_size=2, include_current_message=False)

    # Test message 5 (index 4)
    target_message = messages[4]  # Message ID 5
    context = context_manager.get_context_for_message(target_message)

    # Expected: messages 3, 4, 6, 7 (IDs) - current message 5 is excluded
    expected_ids = [3, 4, 6, 7]
    assert [msg.id for msg in context] == expected_ids
    assert len(context) == 4


def test_get_context_for_message_with_replies():
    messages = create_dummy_messages(10)
    # Message 7 replies to 5
    messages[6].reply_to_message_id = messages[4].id  # Message 7 (index 6) replies to Message 5 (index 4)
    # Message 9 replies to 7
    messages[8].reply_to_message_id = messages[6].id  # Message 9 (index 8) replies to Message 7 (index 6)

    context_manager = SlidingWindowContext(messages, window_size=1, reply_depth=2)

    # Test message 9 (index 8)
    target_message = messages[8]  # Message ID 9
    context = context_manager.get_context_for_message(target_message)

    # Expected:
    # Current: 9
    # Window: 8, 10
    # Reply chain (depth 2): 9 -> 7 -> 5
    # Combined and sorted: 5, 7, 8, 9, 10
    expected_ids = [5, 7, 8, 9, 10]
    assert [msg.id for msg in context] == expected_ids
    assert len(context) == 5


def test_get_context_for_message_with_replies_deeper_depth():
    messages = create_dummy_messages(10)
    messages[6].reply_to_message_id = messages[4].id  # Message 7 replies to 5
    messages[8].reply_to_message_id = messages[6].id  # Message 9 replies to 7
    messages[9].reply_to_message_id = messages[8].id  # Message 10 replies to 9

    context_manager = SlidingWindowContext(messages, window_size=0, reply_depth=3)

    # Test message 10 (index 9)
    target_message = messages[9]  # Message ID 10
    context = context_manager.get_context_for_message(target_message)

    # Expected:
    # Current: 10
    # Window: (none, size 0)
    # Reply chain (depth 3): 10 -> 9 -> 7 -> 5
    # Combined and sorted: 5, 7, 9, 10
    expected_ids = [5, 7, 9, 10]
    assert [msg.id for msg in context] == expected_ids
    assert len(context) == 4


def test_iterate_with_context():
    messages = create_dummy_messages(5)
    context_manager = SlidingWindowContext(messages, window_size=1, reply_depth=0)

    results = []
    for current_msg, context in context_manager.iterate_with_context():
        results.append((current_msg.id, [msg.id for msg in context]))

    # Expected results for window_size=1, reply_depth=0, include_current_message=True
    # Message 1: [1, 2]
    # Message 2: [1, 2, 3]
    # Message 3: [2, 3, 4]
    # Message 4: [3, 4, 5]
    # Message 5: [4, 5]
    expected_results = [
        (1, [1, 2]),
        (2, [1, 2, 3]),
        (3, [2, 3, 4]),
        (4, [3, 4, 5]),
        (5, [4, 5]),
    ]
    assert results == expected_results


def test_empty_message_list():
    context_manager = SlidingWindowContext([], window_size=1)
    assert (
        context_manager.get_context_for_message(
            TelegramMessage(
                id=1,
                type=MessageType.MESSAGE,
                date="2023-01-01T00:00:00",
                date_unixtime="123",
                from_name="Test",
                from_id="test",
                text="test",
            )
        )
        == []
    )
    results = list(context_manager.iterate_with_context())
    assert results == []


def test_message_not_in_list():
    messages = create_dummy_messages(5)
    context_manager = SlidingWindowContext(messages, window_size=1)
    # Create a message not in the original list
    non_existent_message = UserMessage(
        id=99,
        type=MessageType.MESSAGE,
        date=datetime.now().isoformat(),
        date_unixtime=str(int(datetime.now().timestamp())),
        from_name="Ghost",
        from_id="ghost_id",
        text="I don't exist",
    )
    context = context_manager.get_context_for_message(non_existent_message)
    assert context == []


def test_messages_not_sorted_warning(caplog):
    # Configure loguru to send messages to the standard logging module, which caplog intercepts
    handler_id = loguru_logger.add(caplog.handler, format="{message}", level=0)
    try:
        # Create unsorted messages
        messages = [
            UserMessage(
                id=3,
                type=MessageType.MESSAGE,
                date="2023-01-03T00:00:00",
                date_unixtime="123",
                from_name="U3",
                from_id="u3",
                text="M3",
            ),
            UserMessage(
                id=1,
                type=MessageType.MESSAGE,
                date="2023-01-01T00:00:00",
                date_unixtime="123",
                from_name="U1",
                from_id="u1",
                text="M1",
            ),
            UserMessage(
                id=2,
                type=MessageType.MESSAGE,
                date="2023-01-02T00:00:00",
                date_unixtime="123",
                from_name="U2",
                from_id="u2",
                text="M2",
            ),
        ]
        with caplog.at_level(logging.WARNING):  # Use standard logging level
            SlidingWindowContext(messages)
            assert "Messages are not sorted by ID. Context window might not be accurate." in caplog.text
    finally:
        loguru_logger.remove(handler_id)  # Clean up the handler after the test


def test_invalid_message_type():
    with pytest.raises(TypeError, match="All items in 'messages' must be instances of TelegramMessage."):
        SlidingWindowContext(["not a message"])
