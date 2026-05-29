from datetime import datetime

from pydantic import BaseModel

from debate.constants import MIN_ROUNDS


class RoundResult(BaseModel):
    round_number: int
    pro_message: str
    con_message: str
    timestamp: datetime

class RoundManager:
    """Manages debate rounds and transcript."""

    def __init__(self):
        self._current_round = 1
        self._transcript: list[RoundResult] = []

    def increment_round(self) -> int:
        """Increments the round counter and returns the new round number."""
        self._current_round += 1
        return self._current_round

    def add_round_result(self, result: RoundResult):
        """Adds a completed round result to the history."""
        self._transcript.append(result)

    def get_transcript(self) -> list[RoundResult]:
        """Returns the full debate transcript."""
        return self._transcript.copy()

    def has_minimum_rounds(self) -> bool:
        """Checks if the minimum required rounds have been reached."""
        return self._current_round > MIN_ROUNDS
