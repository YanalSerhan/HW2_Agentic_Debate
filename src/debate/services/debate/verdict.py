"""Auto-generated docstring."""

from datetime import datetime

from pydantic import BaseModel

from debate.shared.constants import AgentRole


class Verdict(BaseModel):
    """Auto-generated docstring."""

    session_id: str
    winner: AgentRole
    pro_score: float
    con_score: float
    reasoning: str
    key_winning_arguments: list[str]
    round_count: int
    total_tokens_used: int
    total_cost_usd: float
    timestamp: datetime

    def is_tie(self) -> bool:
        """Auto-generated docstring."""
        return False
