"""DebateSession — launches child processes and runs the debate loop."""
import logging
import multiprocessing
import uuid
from datetime import datetime, timezone

from debate.agents.con_subagent import ConSubagent
from debate.agents.master_agent import MasterAgent
from debate.agents.pro_subagent import ProSubagent
from debate.constants import MIN_ROUNDS, AgentRole, MessageType
from debate.debate.agreement_detector import AgreementDetector
from debate.debate.round_manager import RoundManager, RoundResult
from debate.debate.verdict import Verdict
from debate.ipc.ipc_channel import IPCChannel, IPCTimeoutError
from debate.ipc.message import DebateMessage
from debate.shared.config import ConfigManager
from debate.shared.gatekeeper import ApiGatekeeper

logger = logging.getLogger(__name__)

MAX_AGREEMENT_RETRIES = 2
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
    
    if role == AgentRole.PRO:
        agent = ProSubagent(session_id, position)
    else:
        agent = ConSubagent(session_id, position)

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
        except Exception as e:
            import traceback
            traceback.print_exc()


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

    # ---- process lifecycle ----

    def start_processes(self):
        """Starts the subagent processes."""
        from debate.rag.role_assigner import RoleAssigner
        roles = RoleAssigner().assign_roles(self.topic)
        self.pro_persona = roles["pro"]
        self.con_persona = roles["con"]
        
        self.pro_process = multiprocessing.Process(
            target=_subagent_worker,
            args=(
                AgentRole.PRO, self.session_id,
                f"Support: {self.topic}", self.config, self.gatekeeper,
                self.father_to_pro, self.pro_to_father, self.pro_persona
            ),
            daemon=True,
        )
        self.con_process = multiprocessing.Process(
            target=_subagent_worker,
            args=(
                AgentRole.CON, self.session_id,
                f"Oppose: {self.topic}", self.config, self.gatekeeper,
                self.father_to_con, self.con_to_father, self.con_persona
            ),
            daemon=True,
        )
        self.pro_process.start()
        self.con_process.start()
        timeout_sec = float(self.config.get("timeout_seconds", 30.0))
        self.father.start_watchdog(timeout=timeout_sec, process=self.pro_process)

    def terminate_processes(self):
        """Cleanly terminates the subagent processes."""
        for proc in (self.pro_process, self.con_process):
            if proc and proc.is_alive():
                proc.terminate()
                proc.join()
        self.father.stop_watchdog()

    def _restart_child(self, role: AgentRole) -> bool:
        """Kill and restart one child process.  Returns False on third failure."""
        restart_key = f"_restart_count_{role.value}"
        count = getattr(self, restart_key, 0)
        if count >= MAX_RESTART_ATTEMPTS:
            return False

        if role == AgentRole.PRO:
            proc = self.pro_process
            ch_send, ch_recv = self.father_to_pro, self.pro_to_father
            position = f"Support: {self.topic}"
            persona = getattr(self, "pro_persona", "hitchens")
        else:
            proc = self.con_process
            ch_send, ch_recv = self.father_to_con, self.con_to_father
            position = f"Oppose: {self.topic}"
            persona = getattr(self, "con_persona", "chomsky")

        if proc and proc.is_alive():
            proc.terminate()
            proc.join()

        new_proc = multiprocessing.Process(
            target=_subagent_worker,
            args=(role, self.session_id, position,
                  self.config, self.gatekeeper, ch_send, ch_recv, persona),
            daemon=True,
        )
        new_proc.start()

        if role == AgentRole.PRO:
            self.pro_process = new_proc
        else:
            self.con_process = new_proc

        setattr(self, restart_key, count + 1)
        self.father.log_event("WATCHDOG_KILL", {"agent": role.value, "attempt": count + 1})
        return True

    # ---- debate loop ----

    def _send_topic_to_agent(self, role: AgentRole, round_number: int):
        """Sends the opening topic to an agent."""
        msg = DebateMessage(
            message_id=str(uuid.uuid4()),
            session_id=self.session_id,
            sender=AgentRole.FATHER,
            recipient=role,
            message_type=MessageType.ARGUMENT,
            round_number=round_number,
            content=f"Debate topic: {self.topic}",
            evidence=[],
            timestamp=datetime.now(timezone.utc),
        )
        self.father.send_to_child(role, msg)

    def _request_from_child(
        self, role: AgentRole, expected_type: MessageType, round_number: int,
        timeout: float = 120.0,
    ) -> DebateMessage | None:
        """Try to receive from *role*; restart on timeout up to limit."""
        try:
            return self.father.receive_from_child(role, expected_type, timeout=timeout)
        except (IPCTimeoutError, ValueError):
            self.father.log_event("TIMEOUT", {"agent": role.value, "round": round_number})
            if self._restart_child(role):
                self._send_topic_to_agent(role, round_number)
                try:
                    return self.father.receive_from_child(role, expected_type, timeout=timeout)
                except Exception:
                    pass
            return None

    def run(self) -> Verdict:
        """Execute the full debate loop and return a Verdict."""
        try:
            self.start_processes()

            # STEP 1 — send topic to both agents
            self._send_topic_to_agent(AgentRole.PRO, round_number=1)
            self._send_topic_to_agent(AgentRole.CON, round_number=1)

            for rnd in range(1, self.max_rounds + 1):
                self.father._current_round = rnd

                # 2a — request argument from Pro
                pro_msg = self._request_from_child(
                    AgentRole.PRO, MessageType.ARGUMENT, rnd, timeout=120.0,
                )
                if pro_msg is None:
                    # Forfeit
                    return self._forfeit_verdict(AgentRole.CON, rnd)

                # 2b — forward Pro's argument to Con
                fwd = DebateMessage(
                    message_id=str(uuid.uuid4()),
                    session_id=self.session_id,
                    sender=AgentRole.FATHER,
                    recipient=AgentRole.CON,
                    message_type=MessageType.ARGUMENT,
                    round_number=rnd,
                    content=pro_msg.content,
                    evidence=pro_msg.evidence,
                    timestamp=datetime.now(timezone.utc),
                )
                self.father.send_to_child(AgentRole.CON, fwd)

                # 2c — receive counter-argument from Con (with agreement check)
                con_msg = self._receive_con_with_agreement_check(pro_msg, rnd)
                if con_msg is None:
                    return self._forfeit_verdict(AgentRole.PRO, rnd)

                # 2d — log round result and calculate cost
                pro_usage = pro_msg.metadata.get("usage", {})
                con_usage = con_msg.metadata.get("usage", {})
                
                round_input_tokens = pro_usage.get("input_tokens", 0) + con_usage.get("input_tokens", 0)
                round_output_tokens = pro_usage.get("output_tokens", 0) + con_usage.get("output_tokens", 0)
                self.total_tokens += round_input_tokens + round_output_tokens
                
                round_cost = (round_input_tokens / 1_000_000 * self.input_cost_per_m) + (round_output_tokens / 1_000_000 * self.output_cost_per_m)
                self.total_cost += round_cost
                
                budget_usd = float(self.config.get("budget_usd", 1.0))
                if self.total_cost >= budget_usd * 0.8:
                    if not getattr(self, "_budget_warning_issued", False):
                        logger.warning(f"BUDGET WARNING: 80% of budget (${budget_usd:.2f}) consumed! Current cost: ${self.total_cost:.2f}")
                        self._budget_warning_issued = True
                
                result = RoundResult(
                    round_number=rnd,
                    pro_message=pro_msg.content,
                    con_message=con_msg.content,
                    timestamp=datetime.now(timezone.utc),
                )
                
                pro_score, con_score = self.father.score_round(result)
                result.pro_score = pro_score
                result.con_score = con_score
                
                self.round_manager.add_round_result(result)
                
                if hasattr(self, "on_round") and callable(self.on_round):
                    self.on_round(rnd, pro_msg.content, con_msg.content)
                
                self.father.log_event("ROUND_COMPLETE", {
                    "round": rnd,
                    "input_tokens": round_input_tokens,
                    "output_tokens": round_output_tokens,
                    "cost": round_cost
                })

                # 2e — ping watchdog
                self.father.ping_watchdog()

                # Prepare next round — send Con's counter back to Pro
                if rnd < self.max_rounds:
                    next_msg = DebateMessage(
                        message_id=str(uuid.uuid4()),
                        session_id=self.session_id,
                        sender=AgentRole.FATHER,
                        recipient=AgentRole.PRO,
                        message_type=MessageType.COUNTER_ARGUMENT,
                        round_number=rnd + 1,
                        content=con_msg.content,
                        evidence=con_msg.evidence,
                        timestamp=datetime.now(timezone.utc),
                    )
                    self.father.send_to_child(AgentRole.PRO, next_msg)

            # STEP 4/5 — verdict
            transcript = self.round_manager.get_transcript()
            return self.father.deliver_verdict(
                transcript, 
                total_tokens=self.total_tokens, 
                total_cost=self.total_cost
            )

        finally:
            self.terminate_processes()

    def _receive_con_with_agreement_check(
        self, pro_msg: DebateMessage, rnd: int,
    ) -> DebateMessage | None:
        """Receive from Con; if it agrees with Pro, re-request up to 2 times."""
        for attempt in range(1 + MAX_AGREEMENT_RETRIES):
            con_msg = self._request_from_child(
                AgentRole.CON, MessageType.COUNTER_ARGUMENT, rnd,
            )
            if con_msg is None:
                return None

            if not self.agreement_detector.is_agreeing(pro_msg.content, con_msg.content):
                return con_msg

            self.father.log_event(
                "AGREEMENT_DETECTED",
                {"round": rnd, "attempt": attempt + 1},
            )
            if attempt < MAX_AGREEMENT_RETRIES:
                # Re-send Pro's message to Con to trigger regeneration
                resend = DebateMessage(
                    message_id=str(uuid.uuid4()),
                    session_id=self.session_id,
                    sender=AgentRole.FATHER,
                    recipient=AgentRole.CON,
                    message_type=MessageType.ARGUMENT,
                    round_number=rnd,
                    content=pro_msg.content,
                    evidence=pro_msg.evidence,
                    timestamp=datetime.now(timezone.utc),
                )
                self.father.send_to_child(AgentRole.CON, resend)

        # After max retries, use the last response anyway
        return con_msg

    def _forfeit_verdict(self, winner: AgentRole, rnd: int) -> Verdict:
        """Create a verdict when one side forfeits due to repeated failures."""
        loser = AgentRole.CON if winner == AgentRole.PRO else AgentRole.PRO
        return Verdict(
            session_id=self.session_id,
            winner=winner,
            pro_score=100.0 if winner == AgentRole.PRO else 0.0,
            con_score=100.0 if winner == AgentRole.CON else 0.0,
            reasoning=f"{loser.value} forfeited after repeated failures in round {rnd}.",
            key_winning_arguments=["Opponent forfeited", "Forfeit", "Timeout"],
            round_count=rnd,
            total_tokens_used=self.total_tokens,
            total_cost_usd=self.total_cost,
            timestamp=datetime.now(timezone.utc),
        )

    def get_transcript(self) -> list[RoundResult]:
        return self.round_manager.get_transcript()
