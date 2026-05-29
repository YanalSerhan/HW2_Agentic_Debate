from pydantic import BaseModel
from datetime import datetime

class RoundResult(BaseModel):
    round_number: int
    pro_message: str
    con_message: str
    timestamp: datetime
