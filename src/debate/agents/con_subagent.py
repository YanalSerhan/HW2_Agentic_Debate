from debate.agents.base_subagent import BaseSubagent
from debate.constants import AgentRole
from debate.ipc.message import DebateMessage
from debate.skills.skill_base import SkillBase


class ConSkill(SkillBase):
    def load_prompt(self) -> str:
        # Normally this would load from con_skill.skill.md
        return "You are the Con agent. Identify the weakest link in the opponent's evidence chain."

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
        if message.message_type == message.message_type.VERDICT_REQUEST:
            pass

        if message.message_type == message.message_type.COUNTER_ARGUMENT or message.message_type == message.message_type.ARGUMENT:
            return self.generate_counter_argument(message, message.round_number)

        return self.generate_argument(message.round_number, [])
