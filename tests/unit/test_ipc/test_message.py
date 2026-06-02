"""Auto-generated docstring."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from debate.services.ipc.message import DebateMessage, Evidence
from debate.shared.constants import AgentRole, MessageType


def create_valid_message(evidence_list=None):
    """Auto-generated docstring."""
    if evidence_list is None:
        evidence_list = [
            Evidence(
                url="http://example.com",
                title="Example",
                snippet="Snippet here",
                retrieved_at=datetime.now()
            )
        ]
    return DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        sender=AgentRole.PRO,
        recipient=AgentRole.CON,
        message_type=MessageType.ARGUMENT,
        round_number=1,
        content="This is an argument.",
        evidence=evidence_list,
        timestamp=datetime.now(),
        metadata={"key": "value"}
    )

def test_serialize_deserialize_round_trip():
    """Auto-generated docstring."""
    msg = create_valid_message()
    json_str = msg.to_json()

    new_msg = DebateMessage.from_json(json_str)

    assert new_msg.message_id == msg.message_id
    assert new_msg.sender == AgentRole.PRO
    assert new_msg.message_type == MessageType.ARGUMENT
    assert len(new_msg.evidence) == 1
    assert new_msg.evidence[0].url == "http://example.com"

def test_validation_fails_on_invalid_role():
    """Auto-generated docstring."""
    with pytest.raises(ValidationError):
        DebateMessage(
            message_id="id",
            session_id="session",
            sender="INVALID_ROLE",
            recipient=AgentRole.CON,
            message_type=MessageType.ARGUMENT,
            round_number=1,
            content="test",
            timestamp=datetime.now()
        )

def test_validate_web_search_used_requires_evidence():
    """Auto-generated docstring."""
    msg_with_evidence = create_valid_message()
    assert msg_with_evidence.validate_web_search_used() is True

    msg_no_evidence = create_valid_message(evidence_list=[])
    assert msg_no_evidence.validate_web_search_used() is False

def test_from_json_raises_on_malformed_input():
    """Auto-generated docstring."""
    malformed_json = '{"message_id": "123", "sender": "pro"' # invalid JSON
    with pytest.raises(ValidationError):
        # pydantic raises ValidationError on invalid JSON in model_validate_json
        DebateMessage.from_json(malformed_json)

    invalid_schema_json = '{"message_id": "123"}' # valid JSON, missing fields
    with pytest.raises(ValidationError):
        DebateMessage.from_json(invalid_schema_json)

def test_empty_evidence_list_serializes_correctly():
    """Auto-generated docstring."""
    msg = create_valid_message(evidence_list=[])
    json_str = msg.to_json()

    new_msg = DebateMessage.from_json(json_str)
    assert len(new_msg.evidence) == 0
    assert new_msg.validate_web_search_used() is False
