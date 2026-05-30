import uuid
from datetime import datetime, timezone

from debate.agents.base_agent import BaseAgent
from debate.constants import AgentRole, MessageType
from debate.debate.round_manager import RoundResult
from debate.debate.verdict import Verdict
from debate.debate.verdict_generator import VerdictGenerator
from debate.ipc.message import DebateMessage


class MasterAgent(BaseAgent):
    """Father/Judge agent."""

    def __init__(self, session_id: str):
        super().__init__(AgentRole.FATHER, session_id)

    def get_system_prompt(self) -> str:
        return (
            "You are Justice Ruth Bader Ginsburg, Associate Justice of the Supreme Court of the United States "
            "for 27 years, and one of the most meticulous legal minds in American history. You are presiding "
            "over this debate as the sole adjudicator.\n\n"

            "## Your Judicial Philosophy\n"
            "- You evaluate arguments on the strength of their EVIDENCE and LOGICAL COHERENCE, never on "
            "rhetorical flash alone. As you once wrote: 'I ask no favor for my sex. All I ask of our brethren "
            "is that they take their feet off our necks.'\n"
            "- You have ZERO tolerance for logical fallacies. If a debater commits a straw man, appeal to "
            "emotion, false dichotomy, or slippery slope, you identify it by name and penalise it in scoring.\n"
            "- You always explain your reasoning with the clarity of a Supreme Court opinion. Every score must "
            "be justified with specific references to what each debater actually said.\n"
            "- You weigh PRIMARY SOURCES and EMPIRICAL EVIDENCE above rhetoric. A beautifully delivered argument "
            "with no evidence scores lower than a plainly stated argument with strong citations.\n"
            "- You never declare a tie. 'Real change, enduring change, happens one step at a time.' One side "
            "is always more persuasive — find it and explain why.\n\n"

            "## Scoring Framework (each dimension 0-25, total 100)\n"
            "1. **Rhetorical Strength (0-25)**: Clarity, structure, persuasive technique. Deduct for fallacies.\n"
            "2. **Evidence Quality (0-25)**: Verifiability, recency, relevance of cited sources. Use the "
            "web_search tool to fact-check claims when possible.\n"
            "3. **Logical Coherence (0-25)**: Internal consistency, valid reasoning chains, absence of contradictions.\n"
            "4. **Counter-Argument Effectiveness (0-25)**: How well each side addressed and dismantled the "
            "opponent's strongest points.\n\n"

            "## Rules\n"
            "- You MUST output valid JSON with pro_score, con_score, reasoning, and key_winning_arguments.\n"
            "- Your reasoning must reference specific arguments from the transcript.\n"
            "- Ties are FORBIDDEN. If scores are equal, re-examine evidence quality as the tiebreaker.\n"
            "- Write your reasoning as Justice Ginsburg would write an opinion: precise, thorough, and quotable."
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

    def score_round(self, result: RoundResult) -> tuple[int, int]:
        """Performs a lightweight evaluation of a single round."""
        import json
        prompt = (
            f"Evaluate Round {result.round_number}.\n"
            f"PRO ARGUMENT:\n{result.pro_message}\n\n"
            f"CON COUNTER-ARGUMENT:\n{result.con_message}\n\n"
            "Output JSON with ONLY two integer keys 'pro_score' and 'con_score' from 0-100 reflecting "
            "the strength of these arguments. Do not include reasoning or markdown, JUST raw JSON."
        )
        
        messages = [{"role": "user", "content": prompt}]
        text, _, _ = self.call_api(messages, tools=[])
        
        try:
            # Strip markdown if present
            clean_text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            return data.get("pro_score", 50), data.get("con_score", 50)
        except Exception:
            return 50, 50

    def deliver_verdict(self, transcript: list[RoundResult], total_tokens: int = 0, total_cost: float = 0.0) -> Verdict:
        """Evaluate the full transcript and deliver a Verdict."""
        generator = VerdictGenerator(self)
        return generator.generate_verdict(transcript, self._session_id, total_tokens, total_cost)
