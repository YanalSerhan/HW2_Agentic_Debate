import pytest
from unittest.mock import MagicMock

from debate.agents.base_agent import BaseAgent, WebSearchNotUsedError
from debate.constants import AgentRole
from debate.shared.config import LoggingConfig


class DummyAgent(BaseAgent):
    def process_message(self, message):
        return message

    def get_system_prompt(self):
        return "system prompt"


def _make_agent(client=None):
    agent = DummyAgent(AgentRole.PRO, "session1")
    gatekeeper = MagicMock()
    config = MagicMock()
    config.api_key = None
    config.client = None
    log_config = LoggingConfig(
        version="1.00", log_level="INFO", log_dir="logs",
        max_files=1, max_lines_per_file=5, format="jsonl",
    )
    config.get_logging_config.return_value = log_config
    gatekeeper.execute.side_effect = lambda f, *a, **kw: f(*a, **kw)
    agent.initialize(config, gatekeeper)
    agent._anthropic_client = client
    return agent, gatekeeper


def test_abstract_methods_enforced():
    with pytest.raises(TypeError):
        BaseAgent(AgentRole.PRO, "session1")


def test_call_api_routes_through_gatekeeper():
    agent, gatekeeper = _make_agent()
    text, evidence, usage = agent.call_api([], [])
    gatekeeper.execute.assert_called_once()
    assert text == "Mock response"
    assert len(evidence) == 1


def test_retry_on_missing_search():
    """First failure triggers automatic retry; second failure sets flag."""
    class MockBlock:
        def __init__(self, t, text="Mock text"):
            self.type = t
            self.text = text

    class MockResponseNoTools:
        content = [MockBlock("text")]
        usage = type("o", (object,), {"input_tokens": 10, "output_tokens": 10})()

    client = MagicMock()
    client.messages.create.return_value = MockResponseNoTools()
    agent, _ = _make_agent(client=client)

    text, evidence, usage = agent.call_api([], [])

    # Should have been called twice (original + retry)
    assert client.messages.create.call_count == 2
    # Flag set after two failures
    assert getattr(agent, "_web_search_missing", False) is True
    assert text == "Mock text"
    assert evidence == []


def test_evidence_extracted_from_tool_result():
    agent, _ = _make_agent()
    text, evidence, usage = agent.call_api([], [])
    assert len(evidence) == 1
    assert evidence[0].url == "mock://search"
    assert "mock query" in evidence[0].title
