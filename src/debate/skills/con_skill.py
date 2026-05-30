import os

from debate.skills.skill_base import SkillBase


class ConSkill(SkillBase):
    def load_prompt(self) -> str:
        skill_path = os.path.join(os.path.dirname(__file__), "con_skill.skill.md")
        with open(skill_path, encoding="utf-8") as f:
            return f.read()
