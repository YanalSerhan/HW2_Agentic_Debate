"""Auto-generated docstring."""

from unittest.mock import MagicMock

import pytest

from debate.services.agents.base_agent import BaseAgent
from debate.shared.config import LoggingConfig
from debate.shared.constants import AgentRole


class DummyAgent(BaseAgent):
    """Auto-generated docstring."""

    def process_message(self, message):
        """Auto-generated docstring."""
        return message

    def get_system_prompt(self):
        """Auto-generated docstring."""
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
    """Auto-generated docstring."""
    with pytest.raises(TypeError):
        BaseAgent(AgentRole.PRO, "session1")


def test_call_api_routes_through_gatekeeper(fake_anthropic_client):
    """Auto-generated docstring."""
    agent, rate_limited_gatekeeper = _make_agent(client=fake_anthropic_client)
    text, evidence, usage = agent.call_api([], [])
    assert rate_limited_gatekeeper.execute.called
    assert text == "Mock response"


def test_evidence_extracted_from_tool_result(fake_anthropic_client):
    """Auto-generated docstring."""
    agent, _ = _make_agent(client=fake_anthropic_client)
    text, evidence, usage = agent.call_api([], [])
    assert len(evidence) == 1
    assert evidence[0].url == "mock://search"
    assert "Mock" in evidence[0].title
