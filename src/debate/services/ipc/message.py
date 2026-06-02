"""Auto-generated docstring."""

from datetime import datetime

from pydantic import BaseModel

from debate.shared.constants import AgentRole, MessageType


class Evidence(BaseModel):
    """Auto-generated docstring."""

    url: str
    title: str
    snippet: str
    retrieved_at: datetime

class DebateMessage(BaseModel):
    """Auto-generated docstring."""

    message_id: str
    session_id: str
    sender: AgentRole
    recipient: AgentRole
    message_type: MessageType
    round_number: int
    content: str
    evidence: list[Evidence] = []
    timestamp: datetime
    metadata: dict = {}

    def to_json(self) -> str:
        """Auto-generated docstring."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "DebateMessage":
        """Auto-generated docstring."""
        return cls.model_validate_json(data)

    def validate_web_search_used(self) -> bool:
        """Auto-generated docstring."""
        return len(self.evidence) > 0
