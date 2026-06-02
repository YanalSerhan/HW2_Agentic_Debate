"""Auto-generated docstring."""

from debate.services.agents.base_subagent import BaseSubagent
from debate.services.ipc.message import DebateMessage
from debate.services.skills.pro_skill import ProSkill
from debate.services.skills.skill_base import SkillBase
from debate.shared.constants import AgentRole, MessageType


class ProSubagent(BaseSubagent):
    """Pro position agent."""

    def __init__(self, session_id: str, position: str):
        """Auto-generated docstring."""
        super().__init__(AgentRole.PRO, session_id, position)
        self.persona = "hitchens"
        self._skill = ProSkill()

    def get_skill(self) -> SkillBase:
        """Auto-generated docstring."""
        return self._skill

    def get_system_prompt(self) -> str:
        """Auto-generated docstring."""
        if getattr(self, "persona", "hitchens") == "chomsky":
            from debate.services.skills.con_skill import ConSkill
            self._skill = ConSkill()
        return f"{self._skill.load_prompt()}\nPosition: {self.position}"

    def process_message(self, message: DebateMessage) -> DebateMessage:
        """Auto-generated docstring."""
        if message.message_type == MessageType.VERDICT_REQUEST:
            pass

        return self.generate_argument(message.round_number, [message])
