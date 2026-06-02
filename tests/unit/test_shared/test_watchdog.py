"""Auto-generated docstring."""

import time

from debate.shared.watchdog import WatchdogMixin


class DummyProcess:
    """Auto-generated docstring."""

    def __init__(self):
        """Auto-generated docstring."""
        self.killed = False
        self.alive = True

    def kill(self):
        """Auto-generated docstring."""
        self.killed = True
        self.alive = False

    def is_alive(self):
        """Auto-generated docstring."""
        return self.alive

class DummyAgent(WatchdogMixin):
    """Auto-generated docstring."""

    def __init__(self):
        """Auto-generated docstring."""
        super().__init__()
        self.kill_called = False

    def on_watchdog_kill(self):
        """Auto-generated docstring."""
        self.kill_called = True

def test_watchdog_kills_process_on_timeout():
    """Auto-generated docstring."""
    agent = DummyAgent()
    process = DummyProcess()

    # Tiny timeout for testing
    agent.start_watchdog(timeout=0.1, process=process)

    # Wait for watchdog to trigger
    time.sleep(0.3)

    assert process.killed is True
    assert agent.kill_called is True

    agent.stop_watchdog()

def test_watchdog_reset_prevents_kill():
    """Auto-generated docstring."""
    agent = DummyAgent()
    process = DummyProcess()

    agent.start_watchdog(timeout=0.2, process=process)

    # Ping before timeout
    time.sleep(0.1)
    agent.ping_watchdog()
    time.sleep(0.15)

    # Total time > 0.2, but since we pinged, it shouldn't be killed yet
    assert process.killed is False
    assert agent.kill_called is False

    agent.stop_watchdog()

def test_watchdog_cleans_up_on_stop():
    """Auto-generated docstring."""
    agent = DummyAgent()
    process = DummyProcess()

    agent.start_watchdog(timeout=1.0, process=process)
    agent.stop_watchdog()

    assert agent._watchdog_thread.is_alive() is False
    assert process.killed is False

def test_context_manager_stops_watchdog():
    """Auto-generated docstring."""
    process = DummyProcess()
    with DummyAgent() as agent:
        agent.start_watchdog(timeout=1.0, process=process)
        assert agent._watchdog_thread.is_alive() is True

    # after context manager exits
    assert agent._watchdog_thread.is_alive() is False
    assert process.killed is False
