"""Rate limiting under load tests."""
import time
import threading
import pytest

from debate.shared.config import RateLimitConfig
from debate.shared.gatekeeper import ApiGatekeeper, GatekeeperQueueFullError

def test_gatekeeper_queue_full_under_load():
    config = RateLimitConfig(
        requests_per_minute=100,
        requests_per_hour=100,
        concurrent_max=10,
        retry_after_seconds=1,
        queue_max_depth=3,
        max_retries=1
    )
    gatekeeper = ApiGatekeeper(config)
    
    # Fill the queue up to max depth manually to avoid concurrency hangs
    for _ in range(3):
        gatekeeper.queue.append(object())
        
    with pytest.raises(GatekeeperQueueFullError, match="Queue depth exceeded max depth"):
        gatekeeper.execute(lambda: "fail")
    
def test_gatekeeper_rate_limiting(monkeypatch):
    config = RateLimitConfig(
        requests_per_minute=2,
        requests_per_hour=10,
        concurrent_max=10,
        retry_after_seconds=1,
        queue_max_depth=10,
        max_retries=0
    )
    gatekeeper = ApiGatekeeper(config)
    
    def mock_sleep(secs):
        raise RuntimeError("Rate limited!")
        
    monkeypatch.setattr("time.sleep", mock_sleep)
    
    # Execute 2 calls successfully
    gatekeeper.execute(lambda: "A")
    gatekeeper.execute(lambda: "B")
    
    # 3rd call hits rate limit, gatekeeper tries to sleep.
    with pytest.raises(RuntimeError, match="Rate limited!"):
        gatekeeper.execute(lambda: "C")
