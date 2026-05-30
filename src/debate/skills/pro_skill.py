import os

from debate.skills.skill_base import SkillBase


class ProSkill(SkillBase):
    def load_prompt(self) -> str:
        skill_path = os.path.join(os.path.dirname(__file__), "pro_skill.skill.md")
        with open(skill_path, encoding="utf-8") as f:
            return f.read()
