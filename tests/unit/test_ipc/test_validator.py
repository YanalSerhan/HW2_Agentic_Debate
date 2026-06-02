"""Auto-generated docstring."""

import json
import uuid
from datetime import datetime

from debate.services.ipc.message import DebateMessage
from debate.services.ipc.validator import JSONProtocolValidator
from debate.shared.constants import AgentRole, MessageType


def test_valid_json_passes_validation():
    """Auto-generated docstring."""
    validator = JSONProtocolValidator(AgentRole.PRO)

    msg = DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id="session1",
        sender=AgentRole.PRO,
        recipient=AgentRole.FATHER,
        message_type=MessageType.ARGUMENT,
        round_number=1,
        content="Test content",
        evidence=[],
        timestamp=datetime.now()
    )

    raw = msg.to_json()
    result = validator.validate_message(raw)

    assert result.message_id == msg.message_id
    assert result.message_type == MessageType.ARGUMENT

def test_malformed_json_returns_error_message():
    """Auto-generated docstring."""
    validator = JSONProtocolValidator(AgentRole.PRO)
    raw = '{"broken": "json"'

    result = validator.validate_message(raw)
    assert result.message_type == MessageType.ERROR
    assert "Failed to parse IPC message" in result.content

def test_missing_required_field_returns_error():
    """Auto-generated docstring."""
    validator = JSONProtocolValidator(AgentRole.PRO)
    # Missing session_id, message_type, etc.
    raw = json.dumps({
        "message_id": "123",
        "sender": "pro"
    })

    result = validator.validate_message(raw)
    assert result.message_type == MessageType.ERROR
    assert "Failed to parse IPC message" in result.content
