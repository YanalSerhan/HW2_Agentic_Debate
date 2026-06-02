"""Auto-generated docstring."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from debate.services.agents.con_subagent import ConSubagent
from debate.services.ipc.message import DebateMessage
from debate.shared.config import LoggingConfig
from debate.shared.constants import AgentRole, MessageType


def test_con_subagent_instantiates_and_responds(anthropic_response_factory, fake_anthropic_client):
    """Auto-generated docstring."""
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

def test_con_subagent_hitchens_persona():
    """Auto-generated docstring."""
    agent = ConSubagent(session_id="session1", position="AI is bad")
    agent.persona = "hitchens"
    prompt = agent.get_system_prompt()
    assert "Christopher Hitchens" in prompt

def test_con_subagent_process_message_verdict():
    """Auto-generated docstring."""
    agent = ConSubagent(session_id="session1", position="AI is bad")
    msg = DebateMessage(
        message_id=str(uuid.uuid4()), session_id="s1",
        sender=AgentRole.FATHER, recipient=AgentRole.CON,
        message_type=MessageType.VERDICT_REQUEST, round_number=1,
        content="verdict", evidence=[], timestamp=datetime.now(timezone.utc)
    )
    assert agent.process_message(msg) is None

def test_con_subagent_process_message_counter_argument(monkeypatch):
    """Auto-generated docstring."""
    agent = ConSubagent(session_id="session1", position="AI is bad")
    msg = DebateMessage(
        message_id=str(uuid.uuid4()), session_id="s1",
        sender=AgentRole.FATHER, recipient=AgentRole.CON,
        message_type=MessageType.COUNTER_ARGUMENT, round_number=1,
        content="counter", evidence=[], timestamp=datetime.now(timezone.utc)
    )
    monkeypatch.setattr(agent, "generate_counter_argument", lambda m, r: "generated_counter")
    assert agent.process_message(msg) == "generated_counter"

def test_con_subagent_process_message_default(monkeypatch):
    """Auto-generated docstring."""
    agent = ConSubagent(session_id="session1", position="AI is bad")
    msg = DebateMessage(
        message_id=str(uuid.uuid4()), session_id="s1",
        sender=AgentRole.FATHER, recipient=AgentRole.CON,
        message_type=MessageType.PING, round_number=1,
        content="ping", evidence=[], timestamp=datetime.now(timezone.utc)
    )
    monkeypatch.setattr(agent, "generate_argument", lambda r, e: "generated_arg")
    assert agent.process_message(msg) == "generated_arg"
