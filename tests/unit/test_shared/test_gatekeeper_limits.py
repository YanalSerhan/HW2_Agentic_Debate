"""Auto-generated docstring."""

import time
from unittest.mock import MagicMock

import pytest

from debate.shared.gatekeeper import (
    ApiGatekeeper,
    MaxRetriesExceededError,
    RateLimitConfig,
)


@pytest.fixture
def rate_limit_config():
    """Auto-generated docstring."""
    return RateLimitConfig(
        requests_per_minute=30,
        requests_per_hour=500,
        concurrent_max=3,
        retry_after_seconds=30,
        max_retries=3,
        queue_max_depth=100
    )

def test_retries_on_transient_error(rate_limit_config, monkeypatch):
    """Auto-generated docstring."""
    gatekeeper = ApiGatekeeper(rate_limit_config)

    # Patch time.sleep to avoid waiting during test
    monkeypatch.setattr(time, "sleep", lambda x: None)

    fake_api = MagicMock(side_effect=[Exception("transient"), "success"])

    result = gatekeeper.execute(fake_api)

    assert result == "success"
    assert fake_api.call_count == 2

def test_raises_after_max_retries(rate_limit_config, monkeypatch):
    """Auto-generated docstring."""
    gatekeeper = ApiGatekeeper(rate_limit_config)

    monkeypatch.setattr(time, "sleep", lambda x: None)

    fake_api = MagicMock(side_effect=Exception("persistent error"))

    with pytest.raises(MaxRetriesExceededError, match="API call failed after 3 retries"):
        gatekeeper.execute(fake_api)

    assert fake_api.call_count == 4 # 1 initial + 3 retries
