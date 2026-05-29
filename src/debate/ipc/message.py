from datetime import datetime

from pydantic import BaseModel

from debate.constants import AgentRole, MessageType


class Evidence(BaseModel):
    url: str
    title: str
    snippet: str
    retrieved_at: datetime

class DebateMessage(BaseModel):
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
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "DebateMessage":
        return cls.model_validate_json(data)

    def validate_web_search_used(self) -> bool:
        return len(self.evidence) > 0
