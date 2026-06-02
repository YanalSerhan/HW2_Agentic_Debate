"""Auto-generated docstring."""

import uuid
from datetime import datetime, timezone

from debate.services.ipc.message import DebateMessage
from debate.shared.constants import AgentRole, MessageType
from debate.shared.logging_mixin import LoggingMixin


class JSONProtocolValidator(LoggingMixin):
    """Validates incoming IPC messages, ensuring they are well-formed JSON and adhere to the DebateMessage schema."""

    def __init__(self, agent_role: AgentRole):
        """Auto-generated docstring."""
        super().__init__()
        self._role = agent_role

    def validate_message(self, raw: str) -> DebateMessage:
        """Validates a raw JSON string. If invalid, returns an ERROR message type instead of crashing."""
        try:
            return DebateMessage.from_json(raw)
        except Exception as e:
            # Note: We catch Exception to handle both JSONDecodeError and Pydantic ValidationError
            error_msg = f"Failed to parse IPC message: {str(e)}"

            # Use log_error if logging is set up
            if hasattr(self, '_logger'):
                self.log_error(e, {"raw_message": raw})

            # Create a fallback error message
            return DebateMessage(
                message_id=str(uuid.uuid4()),
                session_id="unknown",
                sender=AgentRole.FATHER, # Defaulting sender since we couldn't parse it
                recipient=self._role,
                message_type=MessageType.ERROR,
                round_number=-1,
                content=error_msg,
                evidence=[],
                timestamp=datetime.now(timezone.utc)
            )
