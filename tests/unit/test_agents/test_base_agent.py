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
    rate_limited_gatekeeper = MagicMock()
    debate_config = MagicMock()
    debate_config.api_key = None
    debate_config.client = None
    log_config = LoggingConfig(
        version="1.00", log_level="INFO", log_dir="logs",
        max_files=1, max_lines_per_file=5, format="jsonl",
    )
    debate_config.get_logging_config.return_value = log_config
    rate_limited_gatekeeper.execute.side_effect = lambda f, *a, **kw: f(*a, **kw)
    agent.initialize(debate_config, rate_limited_gatekeeper)
    agent._anthropic_client = client
    return agent, rate_limited_gatekeeper


def test_abstract_methods_enforced():
    with pytest.raises(TypeError):
        BaseAgent(AgentRole.PRO, "session1")


def test_call_api_routes_through_gatekeeper(fake_anthropic_client):
    agent, rate_limited_gatekeeper = _make_agent(client=fake_anthropic_client)
    text, evidence, usage = agent.call_api([], [])
    assert rate_limited_gatekeeper.execute.called
    assert text == "Mock response"


def test_retry_on_missing_search(anthropic_response_factory, fake_anthropic_client):
    """First failure triggers automatic retry; second failure sets flag."""
    AnthropicContentBlock, AnthropicAPIResponse = anthropic_response_factory

    client = fake_anthropic_client
    # Simulate a response with no tool use blocks
    client.messages.create.side_effect = None
    client.messages.create.return_value = AnthropicAPIResponse([AnthropicContentBlock("text", text="Mock text")])
    agent, _ = _make_agent(client=client)

    text, evidence, usage = agent.call_api([], [])

    # Should have been called twice (original + retry)
    assert client.messages.create.call_count == 2
    # Flag set after two failures
    assert getattr(agent, "_web_search_missing", False) is True
    assert text == "Mock text"
    assert evidence == []


def test_evidence_extracted_from_tool_result(fake_anthropic_client):
    agent, _ = _make_agent(client=fake_anthropic_client)
    text, evidence, usage = agent.call_api([], [])
    assert len(evidence) == 1
    assert evidence[0].url == "mock://search"
    assert "mock" in evidence[0].title
