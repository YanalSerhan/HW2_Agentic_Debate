"""Auto-generated docstring."""

import json

from typer.testing import CliRunner

from debate.cli import app

runner = CliRunner()


def test_transcript_saved_to_results_dir(tmp_path, mocker):
    """Test that running a debate saves a transcript to the output dir."""
    # Mock the SDK to avoid running a real debate
    patched_sdk = mocker.patch("debate.cli.DebateSDK")
    fake_sdk_instance = patched_sdk.return_value

    # Setup mock return values
    from datetime import datetime, timezone

    from debate.services.debate.verdict import Verdict
    from debate.shared.constants import AgentRole

    dummy_verdict = Verdict(
        session_id="test_sess_123",
        winner=AgentRole.PRO,
        pro_score=80.0,
        con_score=70.0,
        reasoning="Good points.",
        key_winning_arguments=["A", "B"],
        round_count=5,
        total_tokens_used=1000,
        total_cost_usd=0.01,
        timestamp=datetime.now(timezone.utc)
    )
    fake_sdk_instance.run_debate.return_value = dummy_verdict
    fake_sdk_instance.get_transcript.return_value = []

    output_dir = tmp_path / "results"

    result = runner.invoke(app, ["run", "--topic", "AI vs Human", "--rounds", "5", "--output-dir", str(output_dir)])

    assert result.exit_code == 0
    assert output_dir.exists()

    # Check if a file was created
    files = list(output_dir.glob("*.json"))
    assert len(files) == 1

    # Check test_transcript_filename_contains_session_id
    assert "test_sess_123" in files[0].name

    # Check test_transcript_is_valid_json
    with open(files[0]) as f:
        data = json.load(f)

    assert data["session_id"] == "test_sess_123"
    assert data["topic"] == "AI vs Human"
    assert "rounds" in data
    assert "verdict" in data
