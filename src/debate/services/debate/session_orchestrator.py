"""Auto-generated docstring."""

import uuid
from datetime import datetime, timezone

from debate.services.debate.verdict import Verdict
from debate.services.ipc.ipc_channel import IPCTimeoutError
from debate.services.ipc.message import DebateMessage
from debate.shared.constants import AgentRole, MessageType

MAX_AGREEMENT_RETRIES = 2

class SessionOrchestrator:
    """Handles communication orchestration for DebateSession."""

    def __init__(self, session):
        """Auto-generated docstring."""
        self.session = session

    def send_topic_to_agent(self, role: AgentRole, round_number: int):
        """Auto-generated docstring."""
        msg = DebateMessage(
            message_id=str(uuid.uuid4()), session_id=self.session.session_id,
            sender=AgentRole.FATHER, recipient=role, message_type=MessageType.ARGUMENT,
            round_number=round_number, content=f"Debate topic: {self.session.topic}",
            evidence=[], timestamp=datetime.now(timezone.utc),
        )
        self.session.father.send_to_child(role, msg)

    def request_from_child(self, role: AgentRole, expected_type: MessageType, round_number: int, timeout: float = 120.0) -> DebateMessage | None:
        """Auto-generated docstring."""
        try:
            return self.session.father.receive_from_child(role, expected_type, timeout=timeout)
        except (IPCTimeoutError, ValueError):
            self.session.father.log_event("TIMEOUT", {"agent": role.value, "round": round_number})
            if self.session.process_manager.restart_child(role):
                self.send_topic_to_agent(role, round_number)
                try:
                    return self.session.father.receive_from_child(role, expected_type, timeout=timeout)
                except Exception:
                    pass
            return None

    def receive_con_with_agreement_check(self, pro_msg: DebateMessage, rnd: int) -> DebateMessage | None:
        """Auto-generated docstring."""
        for attempt in range(1 + MAX_AGREEMENT_RETRIES):
            con_msg = self.request_from_child(AgentRole.CON, MessageType.COUNTER_ARGUMENT, rnd)
            if con_msg is None:
                return None
            if not self.session.agreement_detector.is_agreeing(pro_msg.content, con_msg.content):
                return con_msg
            self.session.father.log_event("AGREEMENT_DETECTED", {"round": rnd, "attempt": attempt + 1})
            if attempt < MAX_AGREEMENT_RETRIES:
                resend = DebateMessage(
                    message_id=str(uuid.uuid4()), session_id=self.session.session_id,
                    sender=AgentRole.FATHER, recipient=AgentRole.CON, message_type=MessageType.ARGUMENT,
                    round_number=rnd, content=pro_msg.content, evidence=pro_msg.evidence,
                    timestamp=datetime.now(timezone.utc),
                )
                self.session.father.send_to_child(AgentRole.CON, resend)
        return con_msg

    def forfeit_verdict(self, winner: AgentRole, rnd: int) -> Verdict:
        """Auto-generated docstring."""
        loser = AgentRole.CON if winner == AgentRole.PRO else AgentRole.PRO
        return Verdict(
            session_id=self.session.session_id, winner=winner,
            pro_score=100.0 if winner == AgentRole.PRO else 0.0,
            con_score=100.0 if winner == AgentRole.CON else 0.0,
            reasoning=f"{loser.value} forfeited after repeated failures in round {rnd}.",
            key_winning_arguments=["Opponent forfeited", "Forfeit", "Timeout"],
            round_count=rnd, total_tokens_used=self.session.total_tokens,
            total_cost_usd=self.session.total_cost, timestamp=datetime.now(timezone.utc),
        )

    def run_single_round(self, rnd: int) -> Verdict | None:
        """Auto-generated docstring."""
        from debate.services.debate.round_manager import RoundResult
        self.session.father._current_round = rnd
        pro_msg = self.request_from_child(AgentRole.PRO, MessageType.ARGUMENT, rnd, timeout=120.0)
        if pro_msg is None:
            return self.forfeit_verdict(AgentRole.CON, rnd)
        fwd = DebateMessage(
            message_id=str(uuid.uuid4()), session_id=self.session.session_id,
            sender=AgentRole.FATHER, recipient=AgentRole.CON, message_type=MessageType.ARGUMENT,
            round_number=rnd, content=pro_msg.content, evidence=pro_msg.evidence,
            timestamp=datetime.now(timezone.utc),
        )
        self.session.father.send_to_child(AgentRole.CON, fwd)
        con_msg = self.receive_con_with_agreement_check(pro_msg, rnd)
        if con_msg is None:
            return self.forfeit_verdict(AgentRole.PRO, rnd)

        pro_usage, con_usage = pro_msg.metadata.get("usage", {}), con_msg.metadata.get("usage", {})
        round_input_tokens = pro_usage.get("input_tokens", 0) + con_usage.get("input_tokens", 0)
        round_output_tokens = pro_usage.get("output_tokens", 0) + con_usage.get("output_tokens", 0)
        self.session.total_tokens += round_input_tokens + round_output_tokens
        round_cost = (round_input_tokens / 1_000_000 * self.session.input_cost_per_m) + (round_output_tokens / 1_000_000 * self.session.output_cost_per_m)
        self.session.total_cost += round_cost

        budget_usd = float(self.session.config.get("budget_usd", 1.0))
        if self.session.total_cost >= budget_usd * 0.8 and not getattr(self.session, "_budget_warning_issued", False):
            import logging
            logging.getLogger(__name__).warning(f"BUDGET WARNING: 80% of budget (${budget_usd:.2f}) consumed! Current cost: ${self.session.total_cost:.2f}")
            self.session._budget_warning_issued = True

        if self.session.total_cost >= budget_usd:
            import logging
            logging.getLogger(__name__).error(f"BUDGET EXCEEDED: Cost ${self.session.total_cost:.2f} >= Budget ${budget_usd:.2f}. Aborting.")
            # Calculate current scores to determine a winner early
            pro_score = sum(r.pro_score for r in self.session.round_manager.get_transcript())
            con_score = sum(r.con_score for r in self.session.round_manager.get_transcript())
            winner = AgentRole.PRO if pro_score > con_score else AgentRole.CON if con_score > pro_score else AgentRole.FATHER

            return Verdict(
                session_id=self.session.session_id, winner=winner,
                pro_score=pro_score, con_score=con_score,
                reasoning=f"Debate aborted because total cost (${self.session.total_cost:.2f}) reached the budget limit (${budget_usd:.2f}).",
                key_winning_arguments=["Budget Limit Reached"],
                round_count=rnd, total_tokens_used=self.session.total_tokens,
                total_cost_usd=self.session.total_cost, timestamp=datetime.now(timezone.utc),
            )

        result = RoundResult(round_number=rnd, pro_message=pro_msg.content, con_message=con_msg.content, timestamp=datetime.now(timezone.utc))
        pro_score, con_score = self.session.father.score_round(result)
        result.pro_score, result.con_score = pro_score, con_score
        self.session.round_manager.add_round_result(result)

        if hasattr(self.session, "on_round") and callable(self.session.on_round):
            self.session.on_round(rnd, pro_msg.content, con_msg.content)

        self.session.father.log_event("ROUND_COMPLETE", {"round": rnd, "input_tokens": round_input_tokens, "output_tokens": round_output_tokens, "cost": round_cost})
        self.session.father.ping_watchdog()

        if rnd < self.session.max_rounds:
            next_msg = DebateMessage(
                message_id=str(uuid.uuid4()), session_id=self.session.session_id,
                sender=AgentRole.FATHER, recipient=AgentRole.PRO, message_type=MessageType.COUNTER_ARGUMENT,
                round_number=rnd + 1, content=con_msg.content, evidence=con_msg.evidence,
                timestamp=datetime.now(timezone.utc),
            )
            self.session.father.send_to_child(AgentRole.PRO, next_msg)
        return None
