import json

from debate.replay.replayer import DebateReplayer


def test_debate_replayer(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)

    transcript = {
        "topic": "Replay Topic",
        "rounds": [
            {"round_number": 1, "pro_message": "Pro arg 1", "con_message": "Con arg 1"}
        ],
        "verdict": {
            "session_id": "test_session",
            "pro_score": 60,
            "con_score": 40,
            "winner": "pro",
            "justification": "Pro won because yes.",
            "reasoning": "Some logic.",
            "key_winning_arguments": ["Arg 1", "Arg 2"],
            "timestamp": "2024-01-01T00:00:00Z",
            "round_count": 1,
            "total_tokens_used": 100,
            "total_cost_usd": 0.01
        }
    }

    p = tmp_path / "replay.json"
    p.write_text(json.dumps(transcript))

    replayer = DebateReplayer()
    replayer.replay(str(p))

    captured = capsys.readouterr().out
    assert "Replay Topic" in captured
    assert "Pro arg 1" in captured
    assert "Con arg 1" in captured
    assert "VERDICT" in captured
    assert "Some logic." in captured

def test_debate_replayer_invalid_file(capsys):
    replayer = DebateReplayer()
    replayer.replay("nonexistent.json")
    captured = capsys.readouterr().out
    assert "Failed to load file" in captured
