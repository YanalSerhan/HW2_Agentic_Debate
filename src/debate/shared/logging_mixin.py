"""Auto-generated docstring."""

import json
import os
import traceback
import uuid
from datetime import datetime, timezone

from debate.shared.config import LoggingConfig


class LineRotatingLogger:
    """A simple line-based rotating JSONL file logger."""

    def __init__(self, log_dir: str, max_files: int, max_lines_per_file: int):
        """Auto-generated docstring."""
        self.log_dir = log_dir
        self.max_files = max_files
        self.max_lines_per_file = max_lines_per_file
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_file = self._get_filename(0)
        if not os.path.exists(self.current_file):
            open(self.current_file, 'w').close()
        self.current_lines = self._count_lines(self.current_file)

    def _get_filename(self, index: int) -> str:
        return os.path.join(self.log_dir, f"debate_{index}.jsonl")

    def _count_lines(self, filepath: str) -> int:
        if not os.path.exists(filepath):
            return 0
        with open(filepath, encoding='utf-8') as f:
            return sum(1 for _ in f)

    def _rotate(self):
        # Shift files up to keep the newest at debate_0.jsonl
        for i in range(self.max_files - 1, 0, -1):
            src = self._get_filename(i - 1)
            dst = self._get_filename(i)
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)

        # create a new empty file at debate_0.jsonl
        self.current_file = self._get_filename(0)
        open(self.current_file, 'w').close()
        self.current_lines = 0

    def write(self, record: dict):
        """Auto-generated docstring."""
        if self.current_lines >= self.max_lines_per_file:
            self._rotate()
        with open(self.current_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
        self.current_lines += 1

class LoggingMixin:
    """Mixin for agent logging."""

    def setup_logging(self, agent_name: str, config: LoggingConfig):
        """Auto-generated docstring."""
        self._agent_name = agent_name
        self._session_id = str(uuid.uuid4()) # default, can be overridden by agent
        self._logger = LineRotatingLogger(
            log_dir=config.log_dir,
            max_files=config.max_files,
            max_lines_per_file=config.max_lines_per_file
        )

    def log_event(self, event_type: str, data: dict):
        """Auto-generated docstring."""
        if not hasattr(self, '_logger'):
            return

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self._agent_name,
            "event_type": event_type,
            "session_id": getattr(self, '_session_id', 'unknown'),
            "round": getattr(self, '_current_round', 0),
            "data": data
        }
        self._logger.write(record)

    def log_api_call(self, prompt_tokens: int, completion_tokens: int, cost_usd: float):
        """Auto-generated docstring."""
        self.log_event("API_CALL", {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost_usd
        })

    def log_error(self, error: Exception, context: dict):
        """Auto-generated docstring."""
        data = {
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "context": context
        }
        self.log_event("ERROR", data)
