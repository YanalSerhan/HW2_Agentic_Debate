"""Immutable project constants."""
from enum import Enum


class AgentRole(Enum):
    FATHER = "father"
    PRO = "pro"
    CON = "con"

class MessageType(Enum):
    ARGUMENT = "argument"
    COUNTER_ARGUMENT = "counter_argument"
    SEARCH_RESULT = "search_result"
    VERDICT_REQUEST = "verdict_request"
    VERDICT = "verdict"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"

class DebateStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    JUDGING = "judging"
    COMPLETE = "complete"
    FAILED = "failed"

MIN_ROUNDS = 10
MAX_FILE_LINES = 500
MAX_LOG_FILES = 20
