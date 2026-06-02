"""Auto-generated docstring."""

import logging
import multiprocessing

from debate.services.agents.con_subagent import ConSubagent
from debate.services.agents.pro_subagent import ProSubagent
from debate.services.ipc.ipc_channel import IPCChannel, IPCTimeoutError
from debate.services.rag.role_assigner import RoleAssigner
from debate.shared.config import ConfigManager
from debate.shared.constants import AgentRole
from debate.shared.gatekeeper import ApiGatekeeper

logger = logging.getLogger(__name__)
MAX_RESTART_ATTEMPTS = 2

def _subagent_worker(
    role: AgentRole,
    session_id: str,
    position: str,
    config: ConfigManager,
    gatekeeper: ApiGatekeeper,
    channel_receive: IPCChannel,
    channel_send: IPCChannel,
    persona: str = None,
):
    """Entry point for subagent processes."""
    from dotenv import load_dotenv
    load_dotenv()

    agent = ProSubagent(session_id, position) if role == AgentRole.PRO else ConSubagent(session_id, position)

    if persona:
        agent.persona = persona

    agent.initialize(config, gatekeeper)
    agent.set_ipc_channel(AgentRole.FATHER, channel_send)

    while True:
        try:
            msg = channel_receive.receive(timeout=5.0)
            reply = agent.process_message(msg)
            if reply:
                agent.send_to_father(reply)
        except IPCTimeoutError:
            pass  # timeout — loop again
        except Exception:
            import traceback
            traceback.print_exc()

class ProcessManager:
    """Manages child processes for debate."""

    def __init__(self, session_id, topic, config, gatekeeper, father, f_to_p, p_to_f, f_to_c, c_to_f):
        """Auto-generated docstring."""
        self.session_id = session_id
        self.topic = topic
        self.config = config
        self.gatekeeper = gatekeeper
        self.father = father
        self.father_to_pro = f_to_p
        self.pro_to_father = p_to_f
        self.father_to_con = f_to_c
        self.con_to_father = c_to_f
        self.pro_process = None
        self.con_process = None

    def start_processes(self):
        """Auto-generated docstring."""
        roles = RoleAssigner().assign_roles(self.topic)
        self.pro_persona = roles["pro"]
        self.con_persona = roles["con"]

        self.pro_process = multiprocessing.Process(
            target=_subagent_worker,
            args=(AgentRole.PRO, self.session_id, f"Support: {self.topic}", self.config, self.gatekeeper, self.father_to_pro, self.pro_to_father, self.pro_persona),
            daemon=True,
        )
        self.con_process = multiprocessing.Process(
            target=_subagent_worker,
            args=(AgentRole.CON, self.session_id, f"Oppose: {self.topic}", self.config, self.gatekeeper, self.father_to_con, self.con_to_father, self.con_persona),
            daemon=True,
        )
        self.pro_process.start()
        self.con_process.start()
        timeout_sec = float(self.config.get("timeout_seconds", 30.0))
        self.father.start_watchdog(timeout=timeout_sec, process=[self.pro_process, self.con_process])

    def terminate_processes(self):
        """Auto-generated docstring."""
        for proc in (self.pro_process, self.con_process):
            if proc and proc.is_alive():
                proc.terminate()
                proc.join()
        self.father.stop_watchdog()

    def restart_child(self, role: AgentRole) -> bool:
        """Auto-generated docstring."""
        restart_key = f"_restart_count_{role.value}"
        count = getattr(self, restart_key, 0)
        if count >= MAX_RESTART_ATTEMPTS:
            return False

        if role == AgentRole.PRO:
            proc, ch_send, ch_recv, position, persona = self.pro_process, self.father_to_pro, self.pro_to_father, f"Support: {self.topic}", getattr(self, "pro_persona", "hitchens")
        else:
            proc, ch_send, ch_recv, position, persona = self.con_process, self.father_to_con, self.con_to_father, f"Oppose: {self.topic}", getattr(self, "con_persona", "chomsky")

        if proc and proc.is_alive():
            proc.terminate()
            proc.join()

        new_proc = multiprocessing.Process(
            target=_subagent_worker,
            args=(role, self.session_id, position, self.config, self.gatekeeper, ch_send, ch_recv, persona), daemon=True,
        )
        new_proc.start()

        if role == AgentRole.PRO:
            self.pro_process = new_proc
        else:
            self.con_process = new_proc

        setattr(self, restart_key, count + 1)
        self.father.log_event("WATCHDOG_KILL", {"agent": role.value, "attempt": count + 1})
        return True
