import pytest
import os
import json
from unittest.mock import patch
from debate.shared.logging_mixin import LoggingMixin, LineRotatingLogger
from debate.shared.config import LoggingConfig

@pytest.fixture
def temp_log_dir(tmp_path):
    return str(tmp_path / "logs")

@pytest.fixture
def log_config(temp_log_dir):
    return LoggingConfig(
        version="1.00",
        log_level="INFO",
        log_dir=temp_log_dir,
        max_files=3,
        max_lines_per_file=5,  # small for testing
        format="jsonl"
    )

class DummyAgent(LoggingMixin):
    def __init__(self, name, config):
        self.setup_logging(name, config)
        self._session_id = "test-session"
        self._current_round = 1

def test_log_file_created_in_log_dir(log_config, temp_log_dir):
    agent = DummyAgent("pro", log_config)
    assert os.path.exists(temp_log_dir)
    assert os.path.exists(os.path.join(temp_log_dir, "debate_0.jsonl"))

def test_log_entry_is_valid_json(log_config, temp_log_dir):
    agent = DummyAgent("pro", log_config)
    agent.log_event("TEST_EVENT", {"key": "value"})
    
    log_file = os.path.join(temp_log_dir, "debate_0.jsonl")
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    assert len(lines) == 1
    record = json.loads(lines[0])
    
    assert record["agent"] == "pro"
    assert record["event_type"] == "TEST_EVENT"
    assert record["session_id"] == "test-session"
    assert record["round"] == 1
    assert record["data"] == {"key": "value"}
    assert "timestamp" in record

def test_rotation_triggered_at_max_lines(log_config, temp_log_dir):
    agent = DummyAgent("pro", log_config)
    
    # max_lines_per_file is 5, write 6 lines
    for i in range(6):
        agent.log_event("TEST_EVENT", {"index": i})
        
    log_file_0 = os.path.join(temp_log_dir, "debate_0.jsonl")
    log_file_1 = os.path.join(temp_log_dir, "debate_1.jsonl")
    
    assert os.path.exists(log_file_1)
    
    with open(log_file_1, "r", encoding="utf-8") as f:
        lines_1 = f.readlines()
    assert len(lines_1) == 5
    
    with open(log_file_0, "r", encoding="utf-8") as f:
        lines_0 = f.readlines()
    assert len(lines_0) == 1
    
    record = json.loads(lines_0[0])
    assert record["data"]["index"] == 5
