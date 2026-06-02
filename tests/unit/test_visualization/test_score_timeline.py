import json

import matplotlib

matplotlib.use('Agg')

from debate.services.visualization.score_timeline import ScoreTimeline


def test_score_timeline_generate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    transcript = {
        "topic": "Test Topic",
        "rounds": [
            {"round_number": 1, "pro_message": "hello world", "con_message": "goodbye world", "pro_score": 60, "con_score": 40},
            {"round_number": 2, "pro_message": "a b c d", "con_message": "e f g h i", "pro_score": 55, "con_score": 45}
        ],
        "verdict": {
            "pro_score": 58,
            "con_score": 42,
            "winner": "PRO"
        }
    }

    p = tmp_path / "test_transcript.json"
    p.write_text(json.dumps(transcript))

    timeline = ScoreTimeline()
    result = timeline.generate(str(p))

    assert "status" not in result
    assert "assets/score_timeline.png" in result["score_timeline"]
    assert "assets/token_usage.png" in result["token_usage"]
    assert "assets/final_verdict.png" in result["final_verdict"]

    assert (tmp_path / "assets" / "score_timeline.png").exists()
    assert (tmp_path / "assets" / "token_usage.png").exists()
    assert (tmp_path / "assets" / "final_verdict.png").exists()

def test_score_timeline_no_rounds(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    transcript = {"topic": "Test", "rounds": []}
    p = tmp_path / "test_empty.json"
    p.write_text(json.dumps(transcript))

    timeline = ScoreTimeline()
    result = timeline.generate(str(p))

    assert result["status"] == "error"
