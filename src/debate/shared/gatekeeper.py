"""API Gatekeeper for rate limiting and queue management."""
import time
from collections import deque
from collections.abc import Callable
from typing import Any

from debate.shared.config import RateLimitConfig


class GatekeeperQueueFullError(Exception):
    """Raised when the gatekeeper queue exceeds max depth."""

    pass

class MaxRetriesExceededError(Exception):
    """Raised when an API call fails after maximum retries."""

    pass

class QueueStatus:
    """Auto-generated docstring."""

    def __init__(self, depth: int, max_depth: int, requests_this_minute: int, requests_this_hour: int):
        """Auto-generated docstring."""
        self.depth = depth
        self.max_depth = max_depth
        self.requests_this_minute = requests_this_minute
        self.requests_this_hour = requests_this_hour

class ApiGatekeeper:
    """Auto-generated docstring."""

    def __init__(self, config: RateLimitConfig):
        """Auto-generated docstring."""
        self.config = config
        self.queue = deque()
        self.request_timestamps = []

    def _clean_window(self, now: float):
        one_hour_ago = now - 3600
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > one_hour_ago]

    def _check_rate_limit(self) -> bool:
        now = time.time()
        self._clean_window(now)
        requests_last_minute = sum(1 for ts in self.request_timestamps if ts > now - 60)
        requests_last_hour = len(self.request_timestamps)

        return (requests_last_minute < self.config.requests_per_minute and
                requests_last_hour < self.config.requests_per_hour)

    def get_queue_status(self) -> QueueStatus:
        """Auto-generated docstring."""
        now = time.time()
        self._clean_window(now)
        requests_last_minute = sum(1 for ts in self.request_timestamps if ts > now - 60)
        requests_last_hour = len(self.request_timestamps)
        return QueueStatus(
            depth=len(self.queue),
            max_depth=self.config.queue_max_depth,
            requests_this_minute=requests_last_minute,
            requests_this_hour=requests_last_hour
        )

    def _process_queue(self):
        # A simple sleep until window resets if we are over rate limit.
        while not self._check_rate_limit():
            time.sleep(0.01)

    def execute(self, api_call: Callable, *args, **kwargs) -> Any:
        """Auto-generated docstring."""
        if len(self.queue) >= self.config.queue_max_depth:
            raise GatekeeperQueueFullError("Queue depth exceeded max depth")

        req = object()
        self.queue.append(req)

        try:
            while self.queue[0] is not req or not self._check_rate_limit():
                self._process_queue()

            self.queue.popleft()
            self.request_timestamps.append(time.time())

            retries = 0
            backoff = [1, 2, 4]

            while retries <= self.config.max_retries:
                try:
                    return api_call(*args, **kwargs)
                except Exception as e:
                    if retries == self.config.max_retries:
                        raise MaxRetriesExceededError(f"API call failed after {self.config.max_retries} retries: {e}") from e
                    time.sleep(backoff[retries] if retries < len(backoff) else backoff[-1])
                    retries += 1
        except Exception:
            if req in self.queue:
                self.queue.remove(req)
            raise
