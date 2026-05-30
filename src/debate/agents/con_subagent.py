from debate.agents.base_subagent import BaseSubagent
from debate.constants import AgentRole, MessageType
from debate.ipc.message import DebateMessage
from debate.skills.con_skill import ConSkill
from debate.skills.skill_base import SkillBase

class ConSubagent(BaseSubagent):
    """Con position agent."""

    def __init__(self, session_id: str, position: str):
        super().__init__(AgentRole.CON, session_id, position)
        self._skill = ConSkill()

    def get_skill(self) -> SkillBase:
        return self._skill

    def get_system_prompt(self) -> str:
        return f"{self._skill.load_prompt()}\nPosition: {self.position}"

    def process_message(self, message: DebateMessage) -> DebateMessage:
        if message.message_type == MessageType.VERDICT_REQUEST:
            pass

        if message.message_type == MessageType.COUNTER_ARGUMENT or message.message_type == MessageType.ARGUMENT:
            return self.generate_counter_argument(message, message.round_number)

        return self.generate_argument(message.round_number, [])
