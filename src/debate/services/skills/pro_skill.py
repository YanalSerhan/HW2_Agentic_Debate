"""Auto-generated docstring."""

import os

from debate.services.skills.skill_base import SkillBase


class ProSkill(SkillBase):
    """Auto-generated docstring."""

    def load_prompt(self) -> str:
        """Auto-generated docstring."""
        skill_path = os.path.join(os.path.dirname(__file__), "pro_skill.skill.md")
        with open(skill_path, encoding="utf-8") as f:
            return f.read()
