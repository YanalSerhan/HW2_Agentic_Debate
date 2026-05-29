import pytest
import uuid
import json
from datetime import datetime

from debate.constants import AgentRole, MessageType
from debate.ipc.message import DebateMessage
from debate.ipc.validator import JSONProtocolValidator

def test_valid_json_passes_validation():
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
    validator = JSONProtocolValidator(AgentRole.PRO)
    raw = '{"broken": "json"'
    
    result = validator.validate_message(raw)
    assert result.message_type == MessageType.ERROR
    assert "Failed to parse IPC message" in result.content

def test_missing_required_field_returns_error():
    validator = JSONProtocolValidator(AgentRole.PRO)
    # Missing session_id, message_type, etc.
    raw = json.dumps({
        "message_id": "123",
        "sender": "pro"
    })
    
    result = validator.validate_message(raw)
    assert result.message_type == MessageType.ERROR
    assert "Failed to parse IPC message" in result.content
