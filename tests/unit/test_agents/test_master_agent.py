import uuid
from datetime import datetime
from unittest.mock import MagicMock

from debate.services.agents.master_agent import MasterAgent
from debate.services.ipc.message import DebateMessage
from debate.shared.config import LoggingConfig
from debate.shared.constants import AgentRole, MessageType


def test_master_agent_instantiates_and_responds():
    agent = MasterAgent(session_id="session1")

    gatekeeper = MagicMock()
    config = MagicMock()
    log_config = LoggingConfig(version="1.00", log_level="INFO", log_dir="logs", max_files=1, max_lines_per_file=5, format="jsonl")
    config.get_logging_config.return_value = log_config

    agent.initialize(config, gatekeeper)

    prompt = agent.get_system_prompt()
    assert "Ruth Bader Ginsburg" in prompt
    assert "never declare a tie" in prompt

    msg = DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id="session1",
        sender=AgentRole.PRO,
        recipient=AgentRole.FATHER,
        message_type=MessageType.ARGUMENT,
        round_number=1,
        content="test",
        timestamp=datetime.now()
    )

    response = agent.process_message(msg)
    assert response.message_type == MessageType.PONG
    assert response.recipient == AgentRole.PRO
