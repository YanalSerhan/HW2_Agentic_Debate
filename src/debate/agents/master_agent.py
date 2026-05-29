import uuid
from datetime import datetime, timezone

from debate.agents.base_agent import BaseAgent
from debate.agents.base_subagent import BaseSubagent
from debate.constants import AgentRole, MessageType
from debate.debate.round_manager import RoundResult
from debate.debate.verdict import Verdict
from debate.ipc.message import DebateMessage


class MasterAgent(BaseAgent):
    """Father/Judge agent."""

    def __init__(self, session_id: str):
        super().__init__(AgentRole.FATHER, session_id)

    def get_system_prompt(self) -> str:
        return (
            "You are the Father agent (Judge). You orchestrate the debate and evaluate arguments by "
            "persuasive power, not factual truth. You must never declare a tie."
        )

    def process_message(self, message: DebateMessage) -> DebateMessage:
        # The Father typically handles routing or processing incoming messages
        # Here we just acknowledge it for simplicity in Phase 3
        return DebateMessage(
            message_id=str(uuid.uuid4()),
            session_id=self._session_id,
            sender=AgentRole.FATHER,
            recipient=message.sender,
            message_type=MessageType.PONG,
            round_number=message.round_number,
            content="Received",
            evidence=[],
            timestamp=datetime.now(timezone.utc)
        )

    def receive_from_child(self, child_role: AgentRole, expected_type: MessageType, timeout: float = 30.0) -> DebateMessage:
        """Receives a message from a child, validating sender and message type."""
        msg = self.receive_message(channel_role=child_role, timeout=timeout)

        if msg.sender != child_role:
            raise ValueError(f"Security: Expected message from {child_role}, but sender claims to be {msg.sender}")

        if msg.recipient != AgentRole.FATHER:
            raise ValueError(f"Security: Message from {child_role} was not addressed to Father (addressed to {msg.recipient})")

        if msg.message_type != expected_type:
            raise ValueError(f"Protocol: Expected {expected_type}, got {msg.message_type}")

        return msg

    def orchestrate_round(self, round_number: int) -> RoundResult:
        """Requests argument from Pro, sends to Con, receives counter, logs round."""
        # This will be fully fleshed out in Phase 5.
        pass

    def request_argument(self, agent: BaseSubagent, context: list[DebateMessage]) -> DebateMessage:
        """Requests an argument from the given agent."""
        pass

    def deliver_to_opponent(self, message: DebateMessage, recipient: BaseSubagent) -> DebateMessage:
        """Forwards an argument to the opposing agent."""
        pass

    def deliver_verdict(self, transcript: list[RoundResult]) -> Verdict:
        """Evaluates the full transcript and delivers a Verdict."""
        pass

    def _score_persuasion(self, messages: list[DebateMessage]) -> dict[AgentRole, float]:
        """Calls API with full transcript, returns scores."""
        # Hardcoded for Phase 3 to satisfy type hints
        return {AgentRole.PRO: 85.0, AgentRole.CON: 80.0}
