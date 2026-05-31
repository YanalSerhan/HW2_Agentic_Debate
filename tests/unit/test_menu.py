from unittest.mock import patch

from debate.menu import run_menu


@patch("debate.menu.Prompt.ask")
@patch("debate.menu.IntPrompt.ask")
@patch("debate.menu.run")
def test_menu_run_debate(mock_run, mock_int_ask, mock_prompt_ask):
    mock_prompt_ask.side_effect = ["1", "Test Topic", "", "5"]
    mock_int_ask.side_effect = [10]

    run_menu()

    mock_run.assert_called_once_with(
        topic="Test Topic", rounds=10, model=None, log_level="INFO", output_dir="results/", verbose=True
    )

@patch("debate.menu.Prompt.ask")
@patch("debate.menu.IntPrompt.ask")
@patch("debate.menu.glob.glob")
@patch("debate.menu.replay")
def test_menu_replay(mock_replay, mock_glob, mock_int_ask, mock_prompt_ask):
    mock_glob.return_value = ["results/file1.json"]
    mock_prompt_ask.side_effect = ["2", "", "5"]
    mock_int_ask.side_effect = [1]
    run_menu()
    mock_replay.assert_called_once_with("results/file1.json")

@patch("debate.menu.Prompt.ask")
@patch("debate.menu.IntPrompt.ask")
@patch("debate.menu.glob.glob")
@patch("debate.menu.visualize")
def test_menu_visualize(mock_viz, mock_glob, mock_int_ask, mock_prompt_ask):
    mock_glob.return_value = ["results/file1.json"]
    mock_prompt_ask.side_effect = ["3", "", "5"]
    mock_int_ask.side_effect = [1]
    run_menu()
    mock_viz.assert_called_once_with("results/file1.json")

@patch("debate.menu.Prompt.ask")
@patch("debate.menu.IntPrompt.ask")
@patch("debate.menu.glob.glob")
@patch("debate.menu.cost")
def test_menu_cost(mock_cost, mock_glob, mock_int_ask, mock_prompt_ask):
    mock_glob.return_value = ["results/file1.json"]
    mock_prompt_ask.side_effect = ["4", "", "5"]
    mock_int_ask.side_effect = [1]
    run_menu()
    mock_cost.assert_called_once_with("results/file1.json")

@patch("debate.menu.Prompt.ask")
@patch("debate.menu.glob.glob")
def test_menu_no_files(mock_glob, mock_prompt_ask):
    mock_glob.return_value = []
    mock_prompt_ask.side_effect = ["2", "", "5"]
    run_menu()

@patch("debate.menu.Prompt.ask")
def test_menu_exit(mock_prompt_ask):
    mock_prompt_ask.side_effect = ["5"]
    run_menu()
