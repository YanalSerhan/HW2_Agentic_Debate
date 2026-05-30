import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from debate.constants import AgentRole, MessageType
from debate.ipc.ipc_channel import IPCChannel, IPCQueueFullError, IPCTimeoutError
from debate.ipc.message import DebateMessage


def create_valid_message():
    return DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        sender=AgentRole.PRO,
        recipient=AgentRole.CON,
        message_type=MessageType.ARGUMENT,
        round_number=1,
        content="This is an argument.",
        evidence=[],
        timestamp=datetime.now(),
        metadata={}
    )

def test_send_receive_round_trip():
    channel = IPCChannel()
    msg = create_valid_message()

    assert channel.is_empty() is True
    channel.send(msg)

    received_msg = channel.receive(timeout=1.0)
    assert received_msg.message_id == msg.message_id
    assert channel.is_empty() is True

def test_receive_raises_on_timeout():
    channel = IPCChannel()

    with pytest.raises(IPCTimeoutError):
        channel.receive(timeout=0.1)

def test_queue_full_raises_backpressure_error():
    # create channel with very small maxsize
    channel = IPCChannel(maxsize=1)
    msg1 = create_valid_message()
    msg2 = create_valid_message()

    channel.send(msg1)

    with pytest.raises(IPCQueueFullError):
        channel.send(msg2)

def test_message_validated_on_receive():
    channel = IPCChannel()
    # intentionally bypass `send` to put invalid json
    channel._queue.put('{"message_id": "123", "invalid": "data"}')

    with pytest.raises(ValidationError):
        channel.receive(timeout=1.0)
