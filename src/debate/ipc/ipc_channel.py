import multiprocessing
import queue

from debate.ipc.message import DebateMessage


class IPCTimeoutError(Exception):
    """Raised when receive operation times out."""
    pass

class IPCQueueFullError(Exception):
    """Raised when send operation fails because queue is full."""
    pass

class IPCChannel:
    """Inter-Process Communication channel based on multiprocessing.Queue."""

    def __init__(self, maxsize: int = 100):
        self._queue = multiprocessing.Queue(maxsize=maxsize)

    def send(self, message: DebateMessage):
        """Serializes and puts message to queue."""
        json_data = message.to_json()
        try:
            # We use a very small timeout for put to ensure it doesn't block indefinitely
            # if the queue is full, allowing us to raise our custom exception.
            self._queue.put(json_data, timeout=0.1)
        except queue.Full as e:
            raise IPCQueueFullError("IPC Channel queue is full") from e

    def receive(self, timeout: float = 30.0) -> DebateMessage:
        """Gets message from queue and deserializes it."""
        try:
            json_data = self._queue.get(timeout=timeout)
            return DebateMessage.from_json(json_data)
        except queue.Empty as e:
            raise IPCTimeoutError(f"No message received within {timeout} seconds") from e

    def is_empty(self) -> bool:
        """Checks if queue is empty."""
        return self._queue.empty()

    def get_depth(self) -> int:
        """Gets approximate depth of queue."""
        return self._queue.qsize()
