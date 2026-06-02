"""Auto-generated docstring."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from debate.services.debate.session import DebateSession
from debate.services.debate.verdict import Verdict
from debate.services.ipc.ipc_channel import IPCChannel, IPCTimeoutError
from debate.services.ipc.message import DebateMessage
from debate.shared.config import ConfigManager
from debate.shared.constants import MIN_ROUNDS, AgentRole, MessageType


def _msg(sender, recipient, mtype, rnd=1, content="test"):
    return DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id="s",
        sender=sender,
        recipient=recipient,
        message_type=mtype,
        round_number=rnd,
        content=content,
        evidence=[],
        timestamp=datetime.now(timezone.utc),
    )

def _make_session(max_rounds=MIN_ROUNDS):
    """Build a DebateSession with mocked child processes (never spawned)."""
    config = ConfigManager("config/")
    from debate.shared.gatekeeper import ApiGatekeeper

    gk = ApiGatekeeper(config.get_rate_limit_config())
    session = DebateSession(
        topic="AI is good", config=config, gatekeeper=gk,
        max_rounds=max_rounds,
    )
    return session

def test_agent_timeout_triggers_restart():
    """When Pro times out the session should attempt a restart."""
    session = _make_session(max_rounds=MIN_ROUNDS)

    call_count = {"n": 0}

    def _pro_recv(timeout=30.0):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise IPCTimeoutError("timeout")
        return _msg(AgentRole.PRO, AgentRole.FATHER, MessageType.ARGUMENT, 1, "recovered")

    con_msgs = iter([
        _msg(AgentRole.CON, AgentRole.FATHER, MessageType.COUNTER_ARGUMENT, r, f"con{r}")
        for r in range(1, MIN_ROUNDS + 1)
    ])

    session.pro_to_father = MagicMock(spec=IPCChannel)
    session.pro_to_father.receive.side_effect = _pro_recv
    session.con_to_father = MagicMock(spec=IPCChannel)
    session.con_to_father.receive.side_effect = lambda timeout=30: next(con_msgs)
    session.father_to_pro = MagicMock(spec=IPCChannel)
    session.father_to_con = MagicMock(spec=IPCChannel)

    session.father.set_ipc_send_channel(AgentRole.PRO, session.father_to_pro)
    session.father.set_ipc_receive_channel(AgentRole.PRO, session.pro_to_father)
    session.father.set_ipc_send_channel(AgentRole.CON, session.father_to_con)
    session.father.set_ipc_receive_channel(AgentRole.CON, session.con_to_father)

    session.process_manager.start_processes = MagicMock()
    session.process_manager.terminate_processes = MagicMock()

    # Stub _restart_child so it doesn't actually spawn a process
    session.process_manager.restart_child = MagicMock(return_value=True)

    verdict = session.run()
    session.process_manager.restart_child.assert_called()
    assert isinstance(verdict, Verdict)

def test_agreement_detection_triggers_regeneration():
    """When Con agrees with Pro the session should re-request."""
    session = _make_session(max_rounds=MIN_ROUNDS)

    con_call = {"n": 0}

    def _con_recv(timeout=30.0):
        con_call["n"] += 1
        rnd = (con_call["n"] + 1) // 2  # two calls per round on first agree
        if con_call["n"] == 1:
            return _msg(AgentRole.CON, AgentRole.FATHER,
                        MessageType.COUNTER_ARGUMENT, 1,
                        "I agree with your assessment entirely.")
        return _msg(AgentRole.CON, AgentRole.FATHER,
                    MessageType.COUNTER_ARGUMENT, rnd,
                    f"Counter argument round {rnd}")

    pro_msgs = iter([
        _msg(AgentRole.PRO, AgentRole.FATHER, MessageType.ARGUMENT, r, f"pro{r}")
        for r in range(1, MIN_ROUNDS + 1)
    ])

    session.pro_to_father = MagicMock(spec=IPCChannel)
    session.pro_to_father.receive.side_effect = lambda timeout=30: next(pro_msgs)
    session.con_to_father = MagicMock(spec=IPCChannel)
    session.con_to_father.receive.side_effect = _con_recv
    session.father_to_pro = MagicMock(spec=IPCChannel)
    session.father_to_con = MagicMock(spec=IPCChannel)

    session.father.set_ipc_send_channel(AgentRole.PRO, session.father_to_pro)
    session.father.set_ipc_receive_channel(AgentRole.PRO, session.pro_to_father)
    session.father.set_ipc_send_channel(AgentRole.CON, session.father_to_con)
    session.father.set_ipc_receive_channel(AgentRole.CON, session.con_to_father)

    session.process_manager.start_processes = MagicMock()
    session.process_manager.terminate_processes = MagicMock()

    verdict = session.run()
    assert isinstance(verdict, Verdict)
    # Con should have received MORE sends than just the rounds (the re-sends)
    assert session.father_to_con.send.call_count > MIN_ROUNDS
