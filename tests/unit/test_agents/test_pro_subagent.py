import pytest
from unittest.mock import MagicMock
from debate.agents.pro_subagent import ProSubagent
from debate.shared.config import LoggingConfig

def test_pro_subagent_instantiates_and_responds():
    agent = ProSubagent(session_id="session1", position="AI is good")
    
    gatekeeper = MagicMock()
    config = MagicMock()
    log_config = LoggingConfig(version="1.00", log_level="INFO", log_dir="logs", max_files=1, max_lines_per_file=5, format="jsonl")
    config.get_logging_config.return_value = log_config
    
    class MockBlock:
        def __init__(self, t, n="", text="Mock text"):
            self.type = t
            self.name = n
            self.text = text
            self.input = {"query": "mock"}
            
    class MockResponse:
        content = [MockBlock("tool_use", "web_search"), MockBlock("text", text="Mock argument")]
        usage = type('obj', (object,), {'input_tokens': 10, 'output_tokens': 10})()
        
    client = MagicMock()
    client.messages.create.return_value = MockResponse()
    
    gatekeeper.execute.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)
    
    agent.initialize(config, gatekeeper, client=client)
    
    # Should use the get_system_prompt in the background via call_api
    prompt = agent.get_system_prompt()
    assert "Pro Skill" in prompt
    assert "AI is good" in prompt
    
    # Test generation
    msg = agent.generate_argument(round_number=1, history=[])
    assert msg.content == "Mock argument"
    assert len(msg.evidence) == 1
    
    # Test agreement check exception
    class MockAgreeResponse:
        content = [MockBlock("tool_use", "web_search"), MockBlock("text", text="I agree with you!")]
        usage = type('obj', (object,), {'input_tokens': 10, 'output_tokens': 10})()
    
    client.messages.create.return_value = MockAgreeResponse()
    from debate.agents.base_subagent import AgreementError
    
    with pytest.raises(AgreementError):
        agent.generate_argument(round_number=2, history=[])
