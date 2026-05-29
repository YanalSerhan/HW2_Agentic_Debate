from pydantic import BaseModel
from datetime import datetime
from typing import List

class Verdict(BaseModel):
    session_id: str
    winner: str
    pro_score: float
    con_score: float
    reasoning: str
    key_winning_arguments: List[str]
    round_count: int
    total_tokens_used: int
    total_cost_usd: float
    timestamp: datetime

    def is_tie(self) -> bool:
        return False
