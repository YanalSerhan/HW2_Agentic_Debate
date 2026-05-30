from debate.agents.base_subagent import BaseSubagent
from debate.constants import AgentRole, MessageType
from debate.ipc.message import DebateMessage
from debate.skills.pro_skill import ProSkill
from debate.skills.skill_base import SkillBase

class ProSubagent(BaseSubagent):
    """Pro position agent."""

    def __init__(self, session_id: str, position: str):
        super().__init__(AgentRole.PRO, session_id, position)
        self._skill = ProSkill()

    def get_skill(self) -> SkillBase:
        return self._skill

    def get_system_prompt(self) -> str:
        return f"{self._skill.load_prompt()}\nPosition: {self.position}"

    def process_message(self, message: DebateMessage) -> DebateMessage:
        if message.message_type == MessageType.VERDICT_REQUEST:
            pass

        return self.generate_argument(message.round_number, [message])
