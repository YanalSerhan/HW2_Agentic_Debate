
import time
from unittest.mock import MagicMock

import pytest

from debate.shared.gatekeeper import (
    ApiGatekeeper,
    GatekeeperQueueFullError,
    RateLimitConfig,
)


@pytest.fixture
def rate_limit_config():
    return RateLimitConfig(
        requests_per_minute=30,
        requests_per_hour=500,
        concurrent_max=3,
        retry_after_seconds=30,
        max_retries=3,
        queue_max_depth=100
    )

def test_execute_calls_api_function(rate_limit_config):
    gatekeeper = ApiGatekeeper(rate_limit_config)
    fake_api = MagicMock(return_value="success")

    result = gatekeeper.execute(fake_api, "arg1", kwarg1="val1")

    assert result == "success"
    fake_api.assert_called_once_with("arg1", kwarg1="val1")

def test_rate_limit_enforced(rate_limit_config, monkeypatch):
    # Set requests_per_minute to 2 to test easily
    config = RateLimitConfig(
        requests_per_minute=2,
        requests_per_hour=500,
        concurrent_max=3,
        retry_after_seconds=30,
        max_retries=3,
        queue_max_depth=100
    )
    gatekeeper = ApiGatekeeper(config)

    fake_api = MagicMock(return_value="success")

    # Fill the rate limit
    gatekeeper.execute(fake_api)
    gatekeeper.execute(fake_api)

    # Next call should queue and process_queue will loop.
    # To avoid infinite loop in tests, we patch time.time to advance it by 61 seconds
    # when _process_queue is called.
    original_time = time.time
    current_time = original_time()

    def fake_time():
        return current_time

    def fake_sleep(seconds):
        nonlocal current_time
        current_time += 61  # advance past the 60s window

    monkeypatch.setattr(time, "time", fake_time)
    monkeypatch.setattr(time, "sleep", fake_sleep)

    gatekeeper.execute(fake_api)

    assert fake_api.call_count == 3
    status = gatekeeper.get_queue_status()
    assert status.requests_this_minute == 1

def test_queue_fills_and_backpressure_triggered(rate_limit_config):
    config = RateLimitConfig(
        requests_per_minute=0, # zero means always rate limited
        requests_per_hour=500,
        concurrent_max=3,
        retry_after_seconds=30,
        max_retries=3,
        queue_max_depth=2 # tiny queue
    )
    gatekeeper = ApiGatekeeper(config)
    fake_api = MagicMock()

    # fill queue manually for test
    gatekeeper.queue.append(object())
    gatekeeper.queue.append(object())

    with pytest.raises(GatekeeperQueueFullError, match="Queue depth exceeded max depth"):
        gatekeeper.execute(fake_api)


def test_queue_status_accurate(rate_limit_config):
    gatekeeper = ApiGatekeeper(rate_limit_config)
    fake_api = MagicMock()

    gatekeeper.execute(fake_api)
    gatekeeper.execute(fake_api)

    status = gatekeeper.get_queue_status()
    assert status.depth == 0
    assert status.max_depth == 100
    assert status.requests_this_minute == 2
    assert status.requests_this_hour == 2

def test_drains_queue_after_window_reset(rate_limit_config, monkeypatch):
    # This is implicitly tested by test_rate_limit_enforced, but let's test that
    # it eventually allows multiple queued items to proceed.
    config = RateLimitConfig(
        requests_per_minute=1,
        requests_per_hour=500,
        concurrent_max=3,
        retry_after_seconds=30,
        max_retries=3,
        queue_max_depth=100
    )
    gatekeeper = ApiGatekeeper(config)

    fake_api = MagicMock(return_value="success")

    gatekeeper.execute(fake_api) # uses the 1 allowed request

    original_time = time.time
    current_time = original_time()

    def fake_time():
        return current_time

    def fake_sleep(seconds):
        nonlocal current_time
        current_time += 61

    monkeypatch.setattr(time, "time", fake_time)
    monkeypatch.setattr(time, "sleep", fake_sleep)

    # This should block, advance time via sleep, and then succeed
    gatekeeper.execute(fake_api)

    assert fake_api.call_count == 2
