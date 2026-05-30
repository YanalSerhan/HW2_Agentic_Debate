from unittest.mock import patch

from debate.menu import run_menu


@patch("debate.menu.Prompt.ask")
@patch("debate.menu.IntPrompt.ask")
@patch("debate.menu.run")
def test_menu_run_debate(mock_run, mock_int_ask, mock_prompt_ask):
    # First choice: "1" (Start), then topic "Test Topic", then wait for enter
    # Second choice: "5" (Exit)
    mock_prompt_ask.side_effect = ["1", "Test Topic", "", "5"]
    mock_int_ask.side_effect = [10]

    run_menu()

    mock_run.assert_called_once_with(
        topic="Test Topic", rounds=10, model=None, log_level="INFO", output_dir="results/", verbose=True
    )

@patch("debate.menu.Prompt.ask")
def test_menu_exit(mock_prompt_ask):
    mock_prompt_ask.side_effect = ["5"]
    run_menu()
    # Should just return cleanly
