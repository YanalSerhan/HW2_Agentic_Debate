from unittest.mock import MagicMock

import pytest

from debate.services.agents.con_subagent import ConSubagent
from debate.shared.config import LoggingConfig


def test_con_subagent_instantiates_and_responds(anthropic_response_factory, fake_anthropic_client):
    AnthropicContentBlock, AnthropicAPIResponse = anthropic_response_factory  # noqa: N806
    agent = ConSubagent(session_id="session1", position="AI is bad")

    rate_limited_gatekeeper = MagicMock()
    debate_config = MagicMock()
    debate_config.api_key = None
    log_config = LoggingConfig(version="1.00", log_level="INFO", log_dir="logs", max_files=1, max_lines_per_file=5, format="jsonl")
    debate_config.get_logging_config.return_value = log_config

    client = fake_anthropic_client
    client.messages.create.side_effect = None
    client.messages.create.return_value = AnthropicAPIResponse([
        AnthropicContentBlock("web_search_tool_result", results=[{"url": "mock://search", "title": "Mock", "snippet": "Mock"}]),
        AnthropicContentBlock("text", text="Mock counter argument")
    ])

    rate_limited_gatekeeper.execute.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)

    agent.initialize(debate_config, rate_limited_gatekeeper)
    agent._anthropic_client = client

    prompt = agent.get_system_prompt()
    assert "Noam Chomsky" in prompt
    assert "AI is bad" in prompt

    msg = agent.generate_argument(round_number=1, history=[])
    assert msg.content == "Mock counter argument"
    assert len(msg.evidence) == 1
