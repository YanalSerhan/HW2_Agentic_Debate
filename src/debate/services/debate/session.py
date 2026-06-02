"""DebateSession — launches child processes and runs the debate loop."""
import logging
import multiprocessing
import uuid

from debate.services.agents.master_agent import MasterAgent
from debate.services.debate.agreement_detector import AgreementDetector
from debate.services.debate.process_manager import ProcessManager
from debate.services.debate.round_manager import RoundManager, RoundResult
from debate.services.debate.session_orchestrator import SessionOrchestrator
from debate.services.debate.verdict import Verdict
from debate.services.ipc.ipc_channel import IPCChannel
from debate.shared.config import ConfigManager
from debate.shared.constants import MIN_ROUNDS, AgentRole
from debate.shared.gatekeeper import ApiGatekeeper

logger = logging.getLogger(__name__)




class DebateSession:
    """Manages the lifecycle of a debate session."""

    def __init__(
        self,
        topic: str,
        config: ConfigManager,
        gatekeeper: ApiGatekeeper,
        max_rounds: int = MIN_ROUNDS,
    ):
        self.session_id = str(uuid.uuid4())
        self.topic = topic
        self.config = config
        self.gatekeeper = gatekeeper
        if max_rounds < MIN_ROUNDS:
            logger.warning(f"Requested {max_rounds} rounds, which is less than MIN_ROUNDS ({MIN_ROUNDS})")
        self.max_rounds = max_rounds

        self.pro_process: multiprocessing.Process | None = None
        self.con_process: multiprocessing.Process | None = None

        # Bidirectional channels — two per child
        self.father_to_pro = IPCChannel()
        self.pro_to_father = IPCChannel()
        self.father_to_con = IPCChannel()
        self.con_to_father = IPCChannel()

        self.father = MasterAgent(self.session_id)
        self.father.initialize(config, gatekeeper)
        self.father.set_ipc_send_channel(AgentRole.PRO, self.father_to_pro)
        self.father.set_ipc_receive_channel(AgentRole.PRO, self.pro_to_father)
        self.father.set_ipc_send_channel(AgentRole.CON, self.father_to_con)
        self.father.set_ipc_receive_channel(AgentRole.CON, self.con_to_father)

        self.round_manager = RoundManager()
        self.agreement_detector = AgreementDetector()

        self.total_tokens = 0
        self.total_cost = 0.0

        pricing = self.config.get("pricing", {})
        self.input_cost_per_m = pricing.get("input_token_cost_per_million", 3.0)
        self.output_cost_per_m = pricing.get("output_token_cost_per_million", 15.0)

        self.process_manager = ProcessManager(
            self.session_id, self.topic, self.config, self.gatekeeper, self.father,
            self.father_to_pro, self.pro_to_father, self.father_to_con, self.con_to_father
        )
        self.orchestrator = SessionOrchestrator(self)



    def run(self) -> Verdict:
        """Execute the full debate loop and return a Verdict."""
        try:
            self.process_manager.start_processes()

            # STEP 1 — send topic to both agents
            self.orchestrator.send_topic_to_agent(AgentRole.PRO, round_number=1)
            self.orchestrator.send_topic_to_agent(AgentRole.CON, round_number=1)

            for rnd in range(1, self.max_rounds + 1):
                verdict = self.orchestrator.run_single_round(rnd)
                if verdict is not None:
                    return verdict

            # STEP 4/5 — verdict
            transcript = self.round_manager.get_transcript()
            return self.father.deliver_verdict(
                transcript,
                total_tokens=self.total_tokens,
                total_cost=self.total_cost
            )

        finally:
            self.process_manager.terminate_processes()

    def get_transcript(self) -> list[RoundResult]:
        return self.round_manager.get_transcript()
