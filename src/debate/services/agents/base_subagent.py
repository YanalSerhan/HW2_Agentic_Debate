import uuid
from abc import abstractmethod
from datetime import datetime, timezone

from debate.services.agents.base_agent import BaseAgent
from debate.services.ipc.message import DebateMessage
from debate.services.rag.retriever import RAGRetriever
from debate.services.skills.skill_base import SkillBase
from debate.shared.constants import AgentRole, MessageType




class BaseSubagent(BaseAgent):
    """Abstract base class for Pro and Con subagents."""

    def __init__(self, role: AgentRole, session_id: str, position: str):
        super().__init__(role, session_id)
        self.position = position
        self.persona = "hitchens" if role == AgentRole.PRO else "chomsky"
        self.retriever = RAGRetriever()

    @abstractmethod
    def get_skill(self) -> SkillBase:
        """Returns agent's unique skill instance."""
        pass

    def _build_argument_prompt(self, round_number: int, history: list[DebateMessage]) -> str:
        history_text = "\n".join([f"Round {m.round_number} ({m.sender.value}): {m.content}" for m in history[-2:]])
        # Retrieve context from knowledge base (assuming topic is self.position for simplicity if topic not provided, or fetch from session)
        # We will just pass self.position as the topic to retrieve relevant chunks
        rag_context = self.retriever.get_context_for_argument(self.persona, self.position, round_number)

        return (
            f"You are defending the position: {self.position}\n"
            f"This is round {round_number}.\n"
            f"{rag_context}"
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



    def generate_argument(self, round_number: int, history: list[DebateMessage]) -> DebateMessage:
        prompt = self._build_argument_prompt(round_number, history)

        messages = [{"role": "user", "content": prompt}]
        text_content, evidence_list, usage_dict = self.call_api(messages, tools=[])



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
