import pytest
import sys
from unittest.mock import MagicMock, patch
from debate.sdk.sdk import DebateSDK

# We create a dummy module to prevent ImportError when SDK tries to import DebateSession
# if the real session.py is just an empty placeholder.
import sys
import types
module_name = 'debate.debate.session'
if module_name not in sys.modules:
    dummy_module = types.ModuleType(module_name)
    dummy_module.DebateSession = MagicMock()
    sys.modules[module_name] = dummy_module

@pytest.fixture
def temp_config_dir(tmp_path):
    import json
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    setup_data = {
        "version": "1.00",
        "model": "test-model",
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

@patch("debate.debate.session.DebateSession")
def test_sdk_initializes_with_valid_topic(patched_session_class, temp_config_dir):
    sdk = DebateSDK(topic="AI is dangerous", config_path=str(temp_config_dir))
    
    assert sdk.topic == "AI is dangerous"
    assert sdk.config_manager is not None
    assert sdk.gatekeeper is not None
    
    patched_session_class.assert_called_once_with(
        topic="AI is dangerous",
        config=sdk.config_manager,
        gatekeeper=sdk.gatekeeper,
        max_rounds=10
    )

@patch("debate.debate.session.DebateSession")
def test_run_debate_returns_verdict(patched_session_class, temp_config_dir):
    fake_session_instance = MagicMock()
    fake_session_instance.run.return_value = "Mocked Verdict"
    patched_session_class.return_value = fake_session_instance
    
    sdk = DebateSDK(topic="AI is dangerous", config_path=str(temp_config_dir))
    result = sdk.run_debate()
    
    assert result == "Mocked Verdict"
    fake_session_instance.run.assert_called_once()

@patch("debate.debate.session.DebateSession")
def test_get_transcript_returns_rounds(patched_session_class, temp_config_dir):
    fake_session_instance = MagicMock()
    fake_session_instance.get_transcript.return_value = ["Round 1", "Round 2"]
    patched_session_class.return_value = fake_session_instance
    
    sdk = DebateSDK(topic="AI is dangerous", config_path=str(temp_config_dir))
    transcript = sdk.get_transcript()
    
    assert transcript == ["Round 1", "Round 2"]
    fake_session_instance.get_transcript.assert_called_once()
