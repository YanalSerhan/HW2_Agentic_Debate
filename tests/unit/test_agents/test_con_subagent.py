import pytest
from unittest.mock import MagicMock
from debate.agents.con_subagent import ConSubagent
from debate.shared.config import LoggingConfig

def test_con_subagent_instantiates_and_responds():
    agent = ConSubagent(session_id="session1", position="AI is bad")
    
    gatekeeper = MagicMock()
    config = MagicMock()
    config.api_key = None
    log_config = LoggingConfig(version="1.00", log_level="INFO", log_dir="logs", max_files=1, max_lines_per_file=5, format="jsonl")
    config.get_logging_config.return_value = log_config
    
    class MockBlock:
        def __init__(self, t, n="", text="Mock text"):
            self.type = t
            self.name = n
            self.text = text
            self.input = {"query": "mock"}
            
    class MockResponse:
        content = [MockBlock("tool_use", "web_search"), MockBlock("text", text="Mock counter argument")]
        usage = type('obj', (object,), {'input_tokens': 10, 'output_tokens': 10})()
        
    client = MagicMock()
    client.messages.create.return_value = MockResponse()
    
    gatekeeper.execute.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)
    
    agent.initialize(config, gatekeeper)
    agent._anthropic_client = client
    
    prompt = agent.get_system_prompt()
    assert "Noam Chomsky" in prompt
    assert "AI is bad" in prompt
    
    msg = agent.generate_argument(round_number=1, history=[])
    assert msg.content == "Mock counter argument"
    assert len(msg.evidence) == 1
