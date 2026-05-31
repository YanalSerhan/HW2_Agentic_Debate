from unittest.mock import MagicMock, patch

from debate.sdk.sdk import DebateSDK, main


def test_sdk_init_with_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")
    sdk = DebateSDK("Test")
    assert sdk.config_manager.api_key == "test_key"

def test_sdk_get_queue_status():
    sdk = DebateSDK("Test")
    status = sdk.get_queue_status()
    assert status.depth == 0

@patch("debate.sdk.sdk.argparse.ArgumentParser.parse_args")
@patch("debate.sdk.sdk.DebateSDK")
def test_sdk_main(mock_sdk_cls, mock_parse_args):
    mock_args = MagicMock()
    mock_args.topic = "Main Topic"
    mock_args.config = "config/"
    mock_parse_args.return_value = mock_args

    mock_sdk = MagicMock()
    mock_sdk.run_debate.return_value = "VERDICT_DATA"
    mock_sdk_cls.return_value = mock_sdk

    main()

    mock_sdk_cls.assert_called_once_with(topic="Main Topic", config_path="config/")
    mock_sdk.run_debate.assert_called_once()

@patch("debate.sdk.sdk.argparse.ArgumentParser.parse_args")
@patch("debate.sdk.sdk.DebateSDK")
def test_sdk_main_exception(mock_sdk_cls, mock_parse_args):
    mock_args = MagicMock()
    mock_parse_args.return_value = mock_args

    mock_sdk = MagicMock()
    mock_sdk.run_debate.side_effect = Exception("Debate error")
    mock_sdk_cls.return_value = mock_sdk

    main()
