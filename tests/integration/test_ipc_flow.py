import multiprocessing
import time
import uuid
from datetime import datetime

import pytest

from debate.services.agents.master_agent import MasterAgent
from debate.services.ipc.ipc_channel import IPCChannel, IPCTimeoutError
from debate.services.ipc.message import DebateMessage
from debate.shared.config import ConfigManager
from debate.shared.constants import AgentRole, MessageType
from debate.shared.gatekeeper import ApiGatekeeper


def create_msg(sender: AgentRole, recipient: AgentRole, msg_type: MessageType):
    return DebateMessage(
        message_id=str(uuid.uuid4()),
        session_id="test",
        sender=sender,
        recipient=recipient,
        message_type=msg_type,
        round_number=1,
        content="Test content",
        evidence=[],
        timestamp=datetime.now()
    )

def dummy_pro_process(receive_channel: IPCChannel, send_channel: IPCChannel):
    # Pro waits for a request, then sends an argument
    try:
        msg = receive_channel.receive(timeout=5.0)
        if msg.message_type == MessageType.ARGUMENT: # Father requesting argument
            reply = create_msg(AgentRole.PRO, AgentRole.FATHER, MessageType.ARGUMENT)
            send_channel.send(reply)
    except Exception:
        pass

def dummy_con_process(receive_channel: IPCChannel, send_channel: IPCChannel):
    try:
        msg = receive_channel.receive(timeout=5.0)
        if msg.message_type == MessageType.ARGUMENT: # Forwarded from Father
            reply = create_msg(AgentRole.CON, AgentRole.FATHER, MessageType.COUNTER_ARGUMENT)
            send_channel.send(reply)
    except Exception:
        pass

def dummy_hanging_process():
    # Process that just hangs indefinitely to test watchdog
    time.sleep(100.0)

def setup_father():
    father = MasterAgent("test")
    config = ConfigManager("config/")

    father.initialize(config, ApiGatekeeper(config.get_rate_limit_config()))
    return father

def test_father_receives_from_pro():
    father = setup_father()
    f_to_p = IPCChannel()
    p_to_f = IPCChannel()

    father.set_ipc_send_channel(AgentRole.PRO, f_to_p)
    father.set_ipc_receive_channel(AgentRole.PRO, p_to_f)

    p = multiprocessing.Process(target=dummy_pro_process, args=(f_to_p, p_to_f))
    p.start()

    try:
        # Father sends request
        req = create_msg(AgentRole.FATHER, AgentRole.PRO, MessageType.ARGUMENT)
        father.send_to_child(AgentRole.PRO, req)

        # Father receives
        reply = father.receive_from_child(AgentRole.PRO, MessageType.ARGUMENT, timeout=2.0)
        assert reply.sender == AgentRole.PRO
        assert reply.message_type == MessageType.ARGUMENT
    finally:
        p.terminate()
        p.join()

def test_father_forwards_to_con():
    father = setup_father()
    f_to_c = IPCChannel()
    c_to_f = IPCChannel()

    father.set_ipc_send_channel(AgentRole.CON, f_to_c)
    father.set_ipc_receive_channel(AgentRole.CON, c_to_f)

    p = multiprocessing.Process(target=dummy_con_process, args=(f_to_c, c_to_f))
    p.start()

    try:
        # Father forwards Pro's argument to Con
        forward_msg = create_msg(AgentRole.FATHER, AgentRole.CON, MessageType.ARGUMENT)
        father.send_to_child(AgentRole.CON, forward_msg)

        # Father receives Con's counter
        reply = father.receive_from_child(AgentRole.CON, MessageType.COUNTER_ARGUMENT, timeout=2.0)
        assert reply.sender == AgentRole.CON
        assert reply.message_type == MessageType.COUNTER_ARGUMENT
    finally:
        p.terminate()
        p.join()

def test_sibling_direct_message_rejected():
    father = setup_father()
    p_to_f = IPCChannel()
    father.set_ipc_receive_channel(AgentRole.PRO, p_to_f)

    # Pro attempts to send a message directly to Con, but puts it on the Father queue
    # because that's its only queue.
    bad_msg = create_msg(AgentRole.PRO, AgentRole.CON, MessageType.ARGUMENT)
    p_to_f.send(bad_msg)

    # Father should reject this because the recipient is not FATHER
    with pytest.raises(ValueError, match="not addressed to Father"):
        father.receive_from_child(AgentRole.PRO, MessageType.ARGUMENT, timeout=1.0)

def test_ipc_timeout_triggers_watchdog():
    father = setup_father()
    p = multiprocessing.Process(target=dummy_hanging_process)
    p.start()

    # Start watchdog with a very short timeout
    father.start_watchdog(timeout=1.0, process=p)

    try:
        # Father attempts to receive but child is hanging
        f_to_p = IPCChannel()
        father.set_ipc_receive_channel(AgentRole.PRO, f_to_p)

        with pytest.raises(IPCTimeoutError):
            father.receive_from_child(AgentRole.PRO, MessageType.ARGUMENT, timeout=1.5)

        # Watchdog should have killed the process
        # Give watchdog thread a moment to run
        time.sleep(0.5)
        assert not p.is_alive()
    finally:
        father.stop_watchdog()
        if p.is_alive():
            p.terminate()
            p.join()
