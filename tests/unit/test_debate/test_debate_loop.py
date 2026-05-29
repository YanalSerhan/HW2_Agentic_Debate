"""Unit tests for the debate loop in DebateSession (Phase 5)."""
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from debate.constants import MIN_ROUNDS, AgentRole, MessageType
from debate.debate.agreement_detector import AgreementDetector
from debate.debate.round_manager import RoundManager, RoundResult
from debate.debate.session import DebateSession
from debate.debate.verdict import Verdict
from debate.ipc.ipc_channel import IPCChannel, IPCTimeoutError
from debate.ipc.message import DebateMessage
from debate.shared.config import ConfigManager


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 5.1 — debate loop tests
# ---------------------------------------------------------------------------

def test_debate_runs_minimum_10_rounds():
    """The round manager should end up with MIN_ROUNDS results."""
    session = _make_session()

    # We mock the IPC so nothing actually spawns processes.
    # Father sends to children via send_to_child → channel.send
    # Father receives via receive_from_child → channel.receive
    pro_replies = []
    con_replies = []
    for rnd in range(1, MIN_ROUNDS + 1):
        pro_replies.append(
            _msg(AgentRole.PRO, AgentRole.FATHER, MessageType.ARGUMENT, rnd,
                 f"Pro argument round {rnd}"),
        )
        con_replies.append(
            _msg(AgentRole.CON, AgentRole.FATHER, MessageType.COUNTER_ARGUMENT, rnd,
                 f"Con counter round {rnd}"),
        )

    pro_idx = {"i": 0}
    con_idx = {"i": 0}

    def _pro_recv(timeout=30.0):
        i = pro_idx["i"]
        pro_idx["i"] += 1
        if i < len(pro_replies):
            return pro_replies[i]
        raise IPCTimeoutError("done")

    def _con_recv(timeout=30.0):
        i = con_idx["i"]
        con_idx["i"] += 1
        if i < len(con_replies):
            return con_replies[i]
        raise IPCTimeoutError("done")

    # Replace channels with mocks
    session.pro_to_father = MagicMock(spec=IPCChannel)
    session.pro_to_father.receive.side_effect = _pro_recv
    session.con_to_father = MagicMock(spec=IPCChannel)
    session.con_to_father.receive.side_effect = _con_recv
    session.father_to_pro = MagicMock(spec=IPCChannel)
    session.father_to_con = MagicMock(spec=IPCChannel)

    # Re-wire father channels
    session.father.set_ipc_send_channel(AgentRole.PRO, session.father_to_pro)
    session.father.set_ipc_receive_channel(AgentRole.PRO, session.pro_to_father)
    session.father.set_ipc_send_channel(AgentRole.CON, session.father_to_con)
    session.father.set_ipc_receive_channel(AgentRole.CON, session.con_to_father)

    # Disable real process spawning
    session.start_processes = MagicMock()
    session.terminate_processes = MagicMock()

    verdict = session.run()

    assert isinstance(verdict, Verdict)
    assert len(session.round_manager.get_transcript()) == MIN_ROUNDS


def test_debate_transcript_length_matches_rounds():
    session = _make_session(max_rounds=MIN_ROUNDS)

    replies_pro = [
        _msg(AgentRole.PRO, AgentRole.FATHER, MessageType.ARGUMENT, r,
             f"arg{r}")
        for r in range(1, MIN_ROUNDS + 1)
    ]
    replies_con = [
        _msg(AgentRole.CON, AgentRole.FATHER, MessageType.COUNTER_ARGUMENT, r,
             f"ctr{r}")
        for r in range(1, MIN_ROUNDS + 1)
    ]

    pro_it = iter(replies_pro)
    con_it = iter(replies_con)

    session.pro_to_father = MagicMock(spec=IPCChannel)
    session.pro_to_father.receive.side_effect = lambda timeout=30: next(pro_it)
    session.con_to_father = MagicMock(spec=IPCChannel)
    session.con_to_father.receive.side_effect = lambda timeout=30: next(con_it)
    session.father_to_pro = MagicMock(spec=IPCChannel)
    session.father_to_con = MagicMock(spec=IPCChannel)

    session.father.set_ipc_send_channel(AgentRole.PRO, session.father_to_pro)
    session.father.set_ipc_receive_channel(AgentRole.PRO, session.pro_to_father)
    session.father.set_ipc_send_channel(AgentRole.CON, session.father_to_con)
    session.father.set_ipc_receive_channel(AgentRole.CON, session.con_to_father)

    session.start_processes = MagicMock()
    session.terminate_processes = MagicMock()

    verdict = session.run()
    transcript = session.get_transcript()
    assert len(transcript) == MIN_ROUNDS
    assert verdict.round_count == MIN_ROUNDS


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

    session.start_processes = MagicMock()
    session.terminate_processes = MagicMock()

    # Stub _restart_child so it doesn't actually spawn a process
    session._restart_child = MagicMock(return_value=True)

    verdict = session.run()
    session._restart_child.assert_called()
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

    session.start_processes = MagicMock()
    session.terminate_processes = MagicMock()

    verdict = session.run()
    assert isinstance(verdict, Verdict)
    # Con should have received MORE sends than just the rounds (the re-sends)
    assert session.father_to_con.send.call_count > MIN_ROUNDS
