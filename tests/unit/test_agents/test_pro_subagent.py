from unittest.mock import MagicMock

import pytest

from debate.services.agents.pro_subagent import ProSubagent
from debate.shared.config import LoggingConfig


def test_pro_subagent_instantiates_and_responds(anthropic_response_factory, fake_anthropic_client):
    AnthropicContentBlock, AnthropicAPIResponse = anthropic_response_factory  # noqa: N806
    agent = ProSubagent(session_id="session1", position="AI is good")

    rate_limited_gatekeeper = MagicMock()
    debate_config = MagicMock()
    debate_config.api_key = None
    log_config = LoggingConfig(version="1.00", log_level="INFO", log_dir="logs", max_files=1, max_lines_per_file=5, format="jsonl")
    debate_config.get_logging_config.return_value = log_config

    client = fake_anthropic_client
    client.messages.create.side_effect = None
    client.messages.create.return_value = AnthropicAPIResponse([
        AnthropicContentBlock("web_search_tool_result", results=[{"url": "mock://search", "title": "Mock", "snippet": "Mock"}]),
        AnthropicContentBlock("text", text="Mock argument")
    ])

    rate_limited_gatekeeper.execute.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)

    agent.initialize(debate_config, rate_limited_gatekeeper)
    agent._anthropic_client = client

    # Should use the get_system_prompt in the background via call_api
    prompt = agent.get_system_prompt()
    assert "Christopher Hitchens" in prompt
    assert "AI is good" in prompt

    # Test generation
    msg = agent.generate_argument(round_number=1, history=[])
    assert msg.content == "Mock argument"
    assert len(msg.evidence) == 1
