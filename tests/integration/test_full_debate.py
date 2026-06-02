"""End-to-end debate (mocked API)."""
import json
import threading
from unittest.mock import patch, MagicMock
from debate.sdk.sdk import DebateSDK
from debate.services.debate.verdict import Verdict

class ThreadProcess:
    """A wrapper to run target in a Thread instead of Process to allow mocks to propagate."""
    def __init__(self, target, args=(), kwargs=None, daemon=None, **kw):
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.thread = threading.Thread(target=self.target, args=self.args, kwargs=self.kwargs)
        self.thread.daemon = daemon if daemon is not None else True
        
    def start(self):
        self.thread.start()
        
    def join(self, timeout=None):
        self.thread.join(timeout=0.1)
        
    def terminate(self):
        pass
        
    def is_alive(self):
        return self.thread.is_alive()

@patch("debate.services.debate.process_manager.multiprocessing.Process", ThreadProcess)
@patch("debate.services.agents.base_agent.BaseAgent._get_client")
def test_full_debate_end_to_end(mock_get_client):
    # Setup mock
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_message = MagicMock()
    def side_effect(*args, **kwargs):
        system_prompt = kwargs.get("system", "")
        if "PRO Subagent" in system_prompt:
            content = json.dumps({"argument": "Pro arg", "sources": []})
        elif "CON Subagent" in system_prompt:
            content = json.dumps({"argument": "Con arg", "sources": []})
        else:
            content = json.dumps({
                "agreement_reached": True,
                "pro_score": 60,
                "con_score": 40,
                "winner": "pro",
                "justification": "Pro won.",
                "reasoning": "Reasons.",
                "key_winning_arguments": []
            })
        
        mock_msg = MagicMock()
        mock_msg.text = content
        # Ensure it has .type = "text" for the api_mixin to parse properly if needed
        mock_msg.type = "text"
        mock_message.content = [mock_msg]
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 10
        return mock_message
        
    mock_client.messages.create.side_effect = side_effect
    
    # Run debate
    sdk = DebateSDK(topic="Mock Topic", max_rounds=3)
    verdict = sdk.run_debate()
    
    assert isinstance(verdict, Verdict)
    assert verdict.winner.value == "pro"
    assert verdict.pro_score == 60
    assert verdict.con_score == 40
    
    transcript = sdk.get_transcript()
    assert len(transcript) > 0
