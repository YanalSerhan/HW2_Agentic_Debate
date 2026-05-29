import uuid
from abc import abstractmethod
from datetime import datetime, timezone

from debate.agents.base_agent import BaseAgent
from debate.constants import AgentRole, MessageType
from debate.ipc.message import DebateMessage
from debate.skills.skill_base import SkillBase


class AgreementError(Exception):
    """Raised when an agent automatically agrees with the opponent."""
    pass

class BaseSubagent(BaseAgent):
    """Abstract base class for Pro and Con subagents."""

    def __init__(self, role: AgentRole, session_id: str, position: str):
        super().__init__(role, session_id)
        self.position = position

    @abstractmethod
    def get_skill(self) -> SkillBase:
        """Returns agent's unique skill instance."""
        pass

    def _build_argument_prompt(self, round_number: int, history: list[DebateMessage]) -> str:
        history_text = "\n".join([f"Round {m.round_number} ({m.sender.value}): {m.content}" for m in history])
        return (
            f"You are defending the position: {self.position}\n"
            f"This is round {round_number}.\n"
            f"Debate history so far:\n{history_text}\n"
            f"Generate your next argument."
        )

    def _build_counter_argument_prompt(self, opponent_message: DebateMessage, round_number: int) -> str:
        return (
            f"You are defending the position: {self.position}\n"
            f"This is round {round_number}.\n"
            f"Your opponent ({opponent_message.sender.value}) said:\n"
            f"{opponent_message.content}\n"
            f"Generate a counter-argument."
        )

    def _check_agreement(self, text: str):
        text_lower = text.lower()
        forbidden_phrases = ["i agree", "you're right", "you are right", "exactly", "correct"]
        for phrase in forbidden_phrases:
            if phrase in text_lower:
                raise AgreementError(f"Agent agreed with opponent using phrase: '{phrase}'")

    def generate_argument(self, round_number: int, history: list[DebateMessage]) -> DebateMessage:
        prompt = self._build_argument_prompt(round_number, history)

        messages = [{"role": "user", "content": prompt}]
        text_content, evidence_list, usage_dict = self.call_api(messages, tools=[])

        self._check_agreement(text_content)

        return DebateMessage(
            message_id=str(uuid.uuid4()),
            session_id=self._session_id,
            sender=self._role,
            recipient=AgentRole.FATHER,
            message_type=MessageType.ARGUMENT,
            round_number=round_number,
            content=text_content,
            evidence=evidence_list,
            timestamp=datetime.now(timezone.utc),
            metadata={"usage": usage_dict}
        )

    def generate_counter_argument(self, opponent_message: DebateMessage, round_number: int) -> DebateMessage:
        prompt = self._build_counter_argument_prompt(opponent_message, round_number)

        messages = [{"role": "user", "content": prompt}]
        text_content, evidence_list, usage_dict = self.call_api(messages, tools=[])

        self._check_agreement(text_content)

        return DebateMessage(
            message_id=str(uuid.uuid4()),
            session_id=self._session_id,
            sender=self._role,
            recipient=AgentRole.FATHER,
            message_type=MessageType.COUNTER_ARGUMENT,
            round_number=round_number,
            content=text_content,
            evidence=evidence_list,
            timestamp=datetime.now(timezone.utc),
            metadata={"usage": usage_dict}
        )
