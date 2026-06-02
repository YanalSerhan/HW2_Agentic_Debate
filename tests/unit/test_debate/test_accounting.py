import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from debate.services.debate.session import DebateSession
from debate.services.ipc.message import DebateMessage
from debate.shared.config import ConfigManager
from debate.shared.constants import AgentRole, MessageType


def _make_msg(role, input_tokens, output_tokens, round_num=1):
    return DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id="s1",
        sender=role,
        recipient=AgentRole.FATHER,
        message_type=MessageType.ARGUMENT if role == AgentRole.PRO else MessageType.COUNTER_ARGUMENT,
        round_number=round_num,
        content="Test content",
        evidence=[],
        timestamp=datetime.now(timezone.utc),
        metadata={"usage": {"input_tokens": input_tokens, "output_tokens": output_tokens}}
    )


def test_token_accumulation_across_rounds():
    config = ConfigManager("config/")
    gatekeeper = MagicMock()

    session = DebateSession("Topic", config, gatekeeper, max_rounds=2)
    session.father = MagicMock()
    session.father.score_round.return_value = (50, 50)

    # Mock _request_from_child to return our constructed messages
    # Round 1: Pro uses 100 in, 50 out. Con uses 150 in, 50 out.
    # Round 2: Pro uses 200 in, 50 out. Con uses 250 in, 50 out.
    msgs = {
        (AgentRole.PRO, 1): _make_msg(AgentRole.PRO, 100, 50, 1),
        (AgentRole.CON, 1): _make_msg(AgentRole.CON, 150, 50, 1),
        (AgentRole.PRO, 2): _make_msg(AgentRole.PRO, 200, 50, 2),
        (AgentRole.CON, 2): _make_msg(AgentRole.CON, 250, 50, 2)
    }

    def simulated_request(role, expected_type, round_number, timeout=30.0):
        return msgs.get((role, round_number))

    session.orchestrator.request_from_child = simulated_request
    session.orchestrator.receive_con_with_agreement_check = lambda pro_msg, rnd: msgs.get((AgentRole.CON, rnd))

    # Disable actual process operations
    session.process_manager.start_processes = MagicMock()
    session.process_manager.terminate_processes = MagicMock()

    # Mock VerdictGenerator call
    session.father.deliver_verdict = MagicMock(return_value="Verdict")

    session.run()

    # Total input: 100 + 150 + 200 + 250 = 700
    # Total output: 50 + 50 + 50 + 50 = 200
    # Total tokens: 900
    assert session.total_tokens == 900


def test_cost_calculation_matches_model_pricing():
    config = ConfigManager("config/")

    # Force specific pricing
    config._setup_config["pricing"] = {
        "input_token_cost_per_million": 3.0,
        "output_token_cost_per_million": 15.0
    }

    gatekeeper = MagicMock()
    session = DebateSession("Topic", config, gatekeeper, max_rounds=1)
    session.father = MagicMock()
    session.father.score_round.return_value = (50, 50)

    # 1 million input tokens, 1 million output tokens for pro
    msgs = {
        (AgentRole.PRO, 1): _make_msg(AgentRole.PRO, 1_000_000, 1_000_000, 1),
        (AgentRole.CON, 1): _make_msg(AgentRole.CON, 0, 0, 1),
    }

    def simulated_request(role, expected_type, round_number, timeout=30.0):
        return msgs.get((role, round_number))

    session.orchestrator.request_from_child = simulated_request
    session.orchestrator.receive_con_with_agreement_check = lambda pro_msg, rnd: msgs.get((AgentRole.CON, rnd))

    session.process_manager.start_processes = MagicMock()
    session.process_manager.terminate_processes = MagicMock()
    session.father.deliver_verdict = MagicMock()

    session.run()

    # 1M input @ $3.0/M = $3.0
    # 1M output @ $15.0/M = $15.0
    # Total cost = $18.0
    assert session.total_cost == 18.0
