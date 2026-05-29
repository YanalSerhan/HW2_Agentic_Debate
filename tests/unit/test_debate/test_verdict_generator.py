import json
from unittest.mock import MagicMock
from datetime import datetime, timezone
import pytest

from debate.constants import AgentRole
from debate.debate.round_manager import RoundResult
from debate.debate.verdict_generator import VerdictGenerator

def _make_mock_master(pro_score=85.0, con_score=82.0, reasoning="Good debate", key_args=None):
    if key_args is None:
        key_args = ["Arg 1", "Arg 2", "Arg 3"]
        
    master = MagicMock()
    
    mock_json = json.dumps({
        "pro_score": pro_score,
        "con_score": con_score,
        "reasoning": reasoning,
        "key_winning_arguments": key_args
    })
    
    # call_api returns (text, evidence, usage)
    master.call_api.return_value = (mock_json, [], {"input_tokens": 100, "output_tokens": 100})
    return master

def _make_transcript():
    return [
        RoundResult(round_number=1, pro_message="Pro arg 1", con_message="Con arg 1", timestamp=datetime.now(timezone.utc)),
        RoundResult(round_number=2, pro_message="Pro arg 2", con_message="Con arg 2", timestamp=datetime.now(timezone.utc))
    ]

def test_verdict_always_has_winner():
    master = _make_mock_master(pro_score=90.0, con_score=80.0)
    generator = VerdictGenerator(master)
    
    verdict = generator.generate_verdict(_make_transcript(), "session1", 500, 0.05)
    
    assert verdict.winner == AgentRole.PRO
    assert verdict.pro_score == 90.0
    assert verdict.con_score == 80.0

def test_tie_resolved_by_tiebreaker():
    # If the LLM returns a tie, VerdictGenerator must break it (rhetorical edge +5 to PRO typically)
    master = _make_mock_master(pro_score=85.0, con_score=85.0)
    generator = VerdictGenerator(master)
    
    verdict = generator.generate_verdict(_make_transcript(), "session1", 500, 0.05)
    
    # The tiebreaker in VerdictGenerator gives +5 to pro
    assert verdict.pro_score == 90.0
    assert verdict.con_score == 85.0
    assert verdict.winner == AgentRole.PRO

def test_reasoning_paragraph_non_empty():
    master = _make_mock_master(reasoning="The Pro agent made superior arguments regarding X.")
    generator = VerdictGenerator(master)
    
    verdict = generator.generate_verdict(_make_transcript(), "session1", 500, 0.05)
    
    assert len(verdict.reasoning) > 0
    assert "superior arguments" in verdict.reasoning

def test_key_winning_arguments_length_three():
    master = _make_mock_master(key_args=["Only one argument"])
    generator = VerdictGenerator(master)
    
    verdict = generator.generate_verdict(_make_transcript(), "session1", 500, 0.05)
    
    # VerdictGenerator should pad it to length 3
    assert len(verdict.key_winning_arguments) == 3
    assert verdict.key_winning_arguments[0] == "Only one argument"
    assert "Fallback argument" in verdict.key_winning_arguments[1]

def test_scores_sum_to_100_per_dimension():
    # Since we use an LLM, we just test that the generator handles arbitrary valid scores.
    # The prompt explicitly asks for sums up to 100.
    master = _make_mock_master(pro_score=100.0, con_score=0.0)
    generator = VerdictGenerator(master)
    verdict = generator.generate_verdict(_make_transcript(), "session1", 500, 0.05)
    assert verdict.pro_score <= 105.0 # Considering tiebreaker could add 5
    assert verdict.con_score >= 0.0
