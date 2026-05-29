import pytest
from unittest.mock import MagicMock
from debate.shared.config import LoggingConfig
from debate.constants import AgentRole
from debate.agents.base_agent import BaseAgent, WebSearchNotUsedError

class DummyAgent(BaseAgent):
    def process_message(self, message):
        return message
        
    def get_system_prompt(self):
        return "system prompt"

def test_abstract_methods_enforced():
    with pytest.raises(TypeError):
        # Cannot instantiate BaseAgent directly due to abstract methods
        BaseAgent(AgentRole.PRO, "session1")

def test_call_api_routes_through_gatekeeper():
    agent = DummyAgent(AgentRole.PRO, "session1")
    gatekeeper = MagicMock()
    config = MagicMock()
    log_config = LoggingConfig(version="1.00", log_level="INFO", log_dir="logs", max_files=1, max_lines_per_file=5, format="jsonl")
    config.get_logging_config.return_value = log_config
    
    # Setup mock gatekeeper to just call the function it's given
    gatekeeper.execute.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)
    
    agent.initialize(config, gatekeeper)
    
    # Call api uses default mock response which includes tool_use
    text, evidence = agent.call_api([], [])
    
    gatekeeper.execute.assert_called_once()
    assert text == "Mock response"
    assert len(evidence) == 1

def test_call_api_raises_if_no_evidence_in_response():
    agent = DummyAgent(AgentRole.PRO, "session1")
    gatekeeper = MagicMock()
    config = MagicMock()
    log_config = LoggingConfig(version="1.00", log_level="INFO", log_dir="logs", max_files=1, max_lines_per_file=5, format="jsonl")
    config.get_logging_config.return_value = log_config
    
    class MockBlock:
        def __init__(self, t, text="Mock text"):
            self.type = t
            self.text = text
            
    class MockResponseNoTools:
        content = [MockBlock("text")]
        usage = type('obj', (object,), {'input_tokens': 10, 'output_tokens': 10})()
        
    client = MagicMock()
    client.messages.create.return_value = MockResponseNoTools()
    
    gatekeeper.execute.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)
    
    agent.initialize(config, gatekeeper, client=client)
    
    with pytest.raises(WebSearchNotUsedError, match="Agent failed to use mandatory web_search tool"):
        agent.call_api([], [])
