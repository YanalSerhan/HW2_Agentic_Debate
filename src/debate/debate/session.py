import multiprocessing
import time
import uuid

from debate.agents.con_subagent import ConSubagent
from debate.agents.master_agent import MasterAgent
from debate.agents.pro_subagent import ProSubagent
from debate.constants import AgentRole
from debate.debate.round_manager import RoundManager, RoundResult
from debate.debate.verdict import Verdict
from debate.ipc.ipc_channel import IPCChannel
from debate.shared.config import ConfigManager
from debate.shared.gatekeeper import ApiGatekeeper


def _subagent_worker(role: AgentRole, session_id: str, position: str, config: ConfigManager,
                     gatekeeper: ApiGatekeeper, channel_receive: IPCChannel, channel_send: IPCChannel):
    """Entry point for subagent processes."""
    if role == AgentRole.PRO:
        agent = ProSubagent(session_id, position)
    else:
        agent = ConSubagent(session_id, position)

    agent.initialize(config, gatekeeper)
    agent.set_ipc_channel(AgentRole.FATHER, channel_send)

    # Simple event loop for Phase 4 validation
    while True:
        try:
            msg = channel_receive.receive(timeout=1.0)
            # Process msg and send reply (dummy logic for now)
            reply = agent.process_message(msg)
            if reply:
                agent.send_to_father(reply)
        except Exception:
            pass # Timeout or other error

class DebateSession:
    """Manages the lifecycle of a debate session."""

    def __init__(self, topic: str, config: ConfigManager, gatekeeper: ApiGatekeeper):
        self.session_id = str(uuid.uuid4())
        self.topic = topic
        self.config = config
        self.gatekeeper = gatekeeper

        self.pro_process = None
        self.con_process = None

        # Channels
        # Father sends to child through father_to_child, child receives from it
        self.father_to_pro = IPCChannel()
        self.pro_to_father = IPCChannel()
        self.father_to_con = IPCChannel()
        self.con_to_father = IPCChannel()

        self.father = MasterAgent(self.session_id)
        self.father.initialize(config, gatekeeper)
        self.father.set_ipc_channel(AgentRole.PRO, self.father_to_pro) # Not exactly right, master sends on father_to_pro but receives on pro_to_father.
        # Actually, standard IPCChannel has only one queue. So we need two channels per child.
        # Let's fix this in IPCMixin logic later or just use two channels.
        # For IPCMixin send_to_child(PRO), it uses self._ipc_channels[PRO].
        # So father's self._ipc_channels[PRO] = father_to_pro (for sending)
        # But for receiving from PRO, father uses pro_to_father.receive()

        self.round_manager = RoundManager()

    def start_processes(self):
        """Starts the subagent processes."""
        self.pro_process = multiprocessing.Process(
            target=_subagent_worker,
            args=(AgentRole.PRO, self.session_id, f"Support: {self.topic}", self.config, self.gatekeeper,
                  self.father_to_pro, self.pro_to_father),
            daemon=True
        )
        self.con_process = multiprocessing.Process(
            target=_subagent_worker,
            args=(AgentRole.CON, self.session_id, f"Oppose: {self.topic}", self.config, self.gatekeeper,
                  self.father_to_con, self.con_to_father),
            daemon=True
        )
        self.pro_process.start()
        self.con_process.start()

        # Start watchdog on master
        self.father.start_watchdog(timeout=30.0, process=self.pro_process)

    def terminate_processes(self):
        """Cleanly terminates the subagent processes."""
        if self.pro_process and self.pro_process.is_alive():
            self.pro_process.terminate()
            self.pro_process.join()
        if self.con_process and self.con_process.is_alive():
            self.con_process.terminate()
            self.con_process.join()
        self.father.stop_watchdog()

    def run(self) -> Verdict:
        """Runs the debate."""
        try:
            self.start_processes()
            # In Phase 5, this will loop rounds. For now just dummy logic.
            time.sleep(1)
            return Verdict(
                session_id=self.session_id, winner=AgentRole.PRO, pro_score=85.0, con_score=80.0,
                reasoning="Mock verdict", key_winning_arguments=[], round_count=1,
                total_tokens_used=100, total_cost_usd=0.0, timestamp=__import__("datetime").datetime.now()
            )
        finally:
            self.terminate_processes()

    def get_transcript(self) -> list[RoundResult]:
        return self.round_manager.get_transcript()
