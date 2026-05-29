import uuid
from datetime import datetime, timezone

from debate.agents.base_agent import BaseAgent
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
        """Requests argument from Pro, sends to Con, receives counter, logs round.

        NOTE: The actual round loop lives in DebateSession.run().  This
        method is kept for direct-call testing.
        """
        return RoundResult(
            round_number=round_number,
            pro_message="",
            con_message="",
            timestamp=datetime.now(timezone.utc),
        )

    def deliver_verdict(self, transcript: list[RoundResult]) -> Verdict:
        """Evaluate the full transcript and deliver a Verdict."""
        scores = self._score_persuasion(transcript)
        pro_score = scores[AgentRole.PRO]
        con_score = scores[AgentRole.CON]

        # Tiebreaker — ties are forbidden
        if pro_score == con_score:
            pro_score += 5.0  # rhetorical-edge tiebreaker

        winner = AgentRole.PRO if pro_score > con_score else AgentRole.CON

        # Pick top 3 winning arguments (simple: longest messages)
        winning_msgs = []
        for r in transcript:
            msg = r.pro_message if winner == AgentRole.PRO else r.con_message
            winning_msgs.append((len(msg), msg[:120]))
        winning_msgs.sort(reverse=True)
        top_args = [m[1] for m in winning_msgs[:3]]

        return Verdict(
            session_id=self._session_id,
            winner=winner,
            pro_score=pro_score,
            con_score=con_score,
            reasoning=(
                f"After {len(transcript)} rounds the {winner.value} agent "
                f"demonstrated stronger persuasive ability."
            ),
            key_winning_arguments=top_args,
            round_count=len(transcript),
            total_tokens_used=0,
            total_cost_usd=0.0,
            timestamp=datetime.now(timezone.utc),
        )

    def _score_persuasion(
        self, transcript: list[RoundResult],
    ) -> dict[AgentRole, float]:
        """Score each side.  Phase 6 will replace this with LLM-based scoring."""
        pro_total = 0.0
        con_total = 0.0
        for r in transcript:
            pro_total += min(len(r.pro_message), 500) / 5.0
            con_total += min(len(r.con_message), 500) / 5.0

        # Normalise to 0-100
        max_score = max(pro_total, con_total, 1.0)
        return {
            AgentRole.PRO: round(pro_total / max_score * 100, 2),
            AgentRole.CON: round(con_total / max_score * 100, 2),
        }
