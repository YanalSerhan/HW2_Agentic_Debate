"""Auto-generated docstring."""

import json

import pytest

from debate.shared.config import ConfigManager, ConfigurationError, LoggingConfig, RateLimitConfig


@pytest.fixture
def temp_config_dir(tmp_path):
    """Auto-generated docstring."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    setup_data = {
        "version": "1.00",
        "model": "claude-sonnet-4-20250514",
        "max_rounds": 10,
        "timeout_seconds": 30,
        "debate_language": "english"
    }

    rate_limits_data = {
        "rate_limits": {
            "version": "1.00",
            "services": {
                "default": {
                    "requests_per_minute": 30,
                    "requests_per_hour": 500,
                    "concurrent_max": 3,
                    "retry_after_seconds": 30,
                    "max_retries": 3,
                    "queue_max_depth": 100
                }
            }
        }
    }

    logging_config_data = {
        "version": "1.00",
        "log_level": "INFO",
        "log_dir": "logs",
        "max_files": 20,
        "max_lines_per_file": 500,
        "format": "jsonl"
    }

    with open(config_dir / "setup.json", "w") as f:
        json.dump(setup_data, f)
    with open(config_dir / "rate_limits.json", "w") as f:
        json.dump(rate_limits_data, f)
    with open(config_dir / "logging_config.json", "w") as f:
        json.dump(logging_config_data, f)

    return config_dir

def test_loads_all_config_files(temp_config_dir):
    """Auto-generated docstring."""
    manager = ConfigManager(config_dir=str(temp_config_dir))

    assert manager.get("model") == "claude-sonnet-4-20250514"
    assert manager.get("max_rounds") == 10
    assert manager.get("timeout_seconds") == 30

    rl_config = manager.get_rate_limit_config()
    assert isinstance(rl_config, RateLimitConfig)
    assert rl_config.requests_per_minute == 30
    assert rl_config.max_retries == 3

    log_config = manager.get_logging_config()
    assert isinstance(log_config, LoggingConfig)
    assert log_config.log_level == "INFO"
    assert log_config.format == "jsonl"

def test_get_returns_default_on_missing_key(temp_config_dir):
    """Auto-generated docstring."""
    manager = ConfigManager(config_dir=str(temp_config_dir))
    assert manager.get("nonexistent_key") is None
    assert manager.get("nonexistent_key", "default_val") == "default_val"

def test_raises_on_missing_required_key(temp_config_dir):
    # Remove a required key
    """Auto-generated docstring."""
    setup_file = temp_config_dir / "setup.json"
    with open(setup_file) as f:
        data = json.load(f)
    del data["model"]
    with open(setup_file, "w") as f:
        json.dump(data, f)

    with pytest.raises(ConfigurationError, match="Missing required key 'model'"):
        ConfigManager(config_dir=str(temp_config_dir))

def test_version_validated_on_load(temp_config_dir, caplog):
    """Version mismatch should log a WARNING and continue (backwards compatible)."""
    import logging

    # Alter version in setup.json
    setup_file = temp_config_dir / "setup.json"
    with open(setup_file) as f:
        data = json.load(f)
    data["version"] = "2.00"
    with open(setup_file, "w") as f:
        json.dump(data, f)

    # Should NOT raise — must remain backwards compatible
    with caplog.at_level(logging.WARNING):
        manager = ConfigManager(config_dir=str(temp_config_dir))

    # Warning must be emitted
    assert any("Version mismatch" in r.message for r in caplog.records)
    # ConfigManager must still be functional
    assert manager.get("max_rounds") == 10
