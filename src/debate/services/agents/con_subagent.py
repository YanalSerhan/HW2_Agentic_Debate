"""Auto-generated docstring."""

from debate.services.agents.base_subagent import BaseSubagent
from debate.services.ipc.message import DebateMessage
from debate.services.skills.con_skill import ConSkill
from debate.services.skills.skill_base import SkillBase
from debate.shared.constants import AgentRole, MessageType


class ConSubagent(BaseSubagent):
    """Con position agent."""

    def __init__(self, session_id: str, position: str):
        """Auto-generated docstring."""
        super().__init__(AgentRole.CON, session_id, position)
        self.persona = "chomsky"
        self._skill = ConSkill()

    def get_skill(self) -> SkillBase:
        """Auto-generated docstring."""
        return self._skill

    def get_system_prompt(self) -> str:
        """Auto-generated docstring."""
        if getattr(self, "persona", "chomsky") == "hitchens":
            from debate.services.skills.pro_skill import ProSkill
            self._skill = ProSkill()
        return f"{self._skill.load_prompt()}\nPosition: {self.position}"

    def process_message(self, message: DebateMessage) -> DebateMessage:
        """Auto-generated docstring."""
        if message.message_type == MessageType.VERDICT_REQUEST:
            return None

        if message.message_type == MessageType.COUNTER_ARGUMENT or message.message_type == MessageType.ARGUMENT:
            return self.generate_counter_argument(message, message.round_number)

        return self.generate_argument(message.round_number, [])
