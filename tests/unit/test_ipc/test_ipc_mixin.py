import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from debate.services.ipc.ipc_mixin import IPCError, IPCMixin
from debate.services.ipc.message import DebateMessage
from debate.shared.constants import AgentRole, MessageType


class DummyAgent(IPCMixin):
    def __init__(self, role):
        super().__init__()
        self._role = role
        self.logged_events = []

    def get_role(self):
        return self._role

    def log_event(self, event_type, data):
        self.logged_events.append((event_type, data))

def create_message(sender, recipient):
    return DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id="session",
        sender=sender,
        recipient=recipient,
        message_type=MessageType.ARGUMENT,
        round_number=1,
        content="test",
        timestamp=datetime.now()
    )

def test_send_to_father_success():
    agent = DummyAgent(AgentRole.PRO)
    channel = MagicMock()
    agent.set_ipc_channel(AgentRole.FATHER, channel)

    msg = create_message(AgentRole.PRO, AgentRole.FATHER)
    agent.send_to_father(msg)

    channel.send.assert_called_once_with(msg)
    assert len(agent.logged_events) == 1
    assert agent.logged_events[0][0] == "IPC_SEND"

def test_send_to_father_fails_if_father():
    agent = DummyAgent(AgentRole.FATHER)
    msg = create_message(AgentRole.FATHER, AgentRole.FATHER)

    with pytest.raises(IPCError, match="Father cannot send to itself"):
        agent.send_to_father(msg)

def test_send_to_father_fails_invalid_routing():
    agent = DummyAgent(AgentRole.PRO)
    agent.set_ipc_channel(AgentRole.FATHER, MagicMock())

    msg = create_message(AgentRole.PRO, AgentRole.CON) # Trying to send to CON via send_to_father
    with pytest.raises(IPCError, match="Child attempted to send direct to AgentRole.CON"):
        agent.send_to_father(msg)

def test_send_to_child_success():
    father = DummyAgent(AgentRole.FATHER)
    pro_channel = MagicMock()
    father.set_ipc_channel(AgentRole.PRO, pro_channel)

    msg = create_message(AgentRole.FATHER, AgentRole.PRO)
    father.send_to_child(AgentRole.PRO, msg)

    pro_channel.send.assert_called_once_with(msg)
    assert len(father.logged_events) == 1

def test_send_to_child_fails_if_not_father():
    child = DummyAgent(AgentRole.PRO)
    msg = create_message(AgentRole.PRO, AgentRole.CON)

    with pytest.raises(IPCError, match="Only Father can use send_to_child"):
        child.send_to_child(AgentRole.CON, msg)

def test_receive_message():
    agent = DummyAgent(AgentRole.FATHER)
    channel = MagicMock()
    msg = create_message(AgentRole.PRO, AgentRole.FATHER)
    channel.receive.return_value = msg
    agent.set_ipc_channel(AgentRole.PRO, channel)

    received = agent.receive_message(AgentRole.PRO, timeout=1.0)

    assert received == msg
    channel.receive.assert_called_once_with(timeout=1.0)
    assert len(agent.logged_events) == 1
    assert agent.logged_events[0][0] == "IPC_RECV"
