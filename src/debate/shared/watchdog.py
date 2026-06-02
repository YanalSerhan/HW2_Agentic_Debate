import threading
import time
from typing import Any


class WatchdogMixin:
    """Mixin for monitoring child processes with a timeout."""

    def __init__(self):
        self._watchdog_thread = None
        self._watchdog_stop_event = threading.Event()
        self._last_ping = 0.0
        self._timeout = 30.0
        self._processes = []

    def start_watchdog(self, timeout: float, process: Any | list[Any]):
        """Starts background daemon thread monitoring processes."""
        self._timeout = timeout
        if isinstance(process, list):
            self._processes = process
        else:
            self._processes = [process] if process else []
            
        self._last_ping = time.time()
        self._watchdog_stop_event.clear()

        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name="WatchdogThread"
        )
        self._watchdog_thread.start()

    def ping_watchdog(self):
        """Resets watchdog timer."""
        self._last_ping = time.time()

    def stop_watchdog(self):
        """Cleanly stops watchdog thread."""
        self._watchdog_stop_event.set()
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            self._watchdog_thread.join(timeout=2.0)

    def _watchdog_loop(self):
        """Kills processes if timeout exceeded, logs kill event, triggers restart."""
        while not self._watchdog_stop_event.is_set():
            time.sleep(0.1)

            # If all processes have naturally terminated, we can just stop
            alive_procs = [p for p in self._processes if hasattr(p, 'is_alive') and p.is_alive()]
            if not alive_procs and self._processes:
                break

            time_since_ping = time.time() - self._last_ping
            if time_since_ping > self._timeout:
                for p in alive_procs:
                    if hasattr(p, 'kill'):
                        p.kill()
                    elif hasattr(p, 'terminate'):
                        p.terminate()
                self.on_watchdog_kill()
                break

    def on_watchdog_kill(self):
        """Override in subclass for custom behavior."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_watchdog()
