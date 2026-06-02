"""Auto-generated docstring."""

from abc import ABC, abstractmethod


class SkillBase(ABC):
    """Abstract base class for agent skills."""

    @abstractmethod
    def load_prompt(self) -> str:
        """Auto-generated docstring."""
        pass
