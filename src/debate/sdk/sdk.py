from dotenv import load_dotenv
load_dotenv()

import argparse
import os
from typing import Any

from anthropic import Anthropic
from debate.shared.config import ConfigManager
from debate.shared.gatekeeper import ApiGatekeeper, QueueStatus


class DebateSDK:
    """Main entry point for the Multi-Agent AI Debate System."""

    def __init__(self, topic: str, config_path: str = "config/", max_rounds: int = 10):
        self.topic = topic
        self.max_rounds = max_rounds
        self.config_manager = ConfigManager(config_dir=config_path)
        
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self.config_manager.api_key = api_key
            
        self.gatekeeper = ApiGatekeeper(self.config_manager.get_rate_limit_config())
        self.on_round = None

        # Late import to allow Phase 2 tests to pass without fully implementing Phase 4
        from debate.debate.session import DebateSession
        self.session = DebateSession(
            topic=self.topic,
            config=self.config_manager,
            gatekeeper=self.gatekeeper,
            max_rounds=self.max_rounds,
        )

    def run_debate(self) -> Any:
        """Orchestrates the full debate and returns a structured verdict."""
        if hasattr(self, "on_round"):
            self.session.on_round = self.on_round
        return self.session.run()

    def get_transcript(self) -> list[Any]:
        """Returns all debate rounds."""
        return self.session.get_transcript()

    def get_queue_status(self) -> QueueStatus:
        """Delegates to gatekeeper."""
        return self.gatekeeper.get_queue_status()

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent AI Debate System")
    parser.add_argument("topic", type=str, help="The debate topic")
    parser.add_argument("--config", type=str, default="config/", help="Path to config directory")
    args = parser.parse_args()

    print(f"Starting debate on topic: {args.topic}")
    sdk = DebateSDK(topic=args.topic, config_path=args.config)
    try:
        verdict = sdk.run_debate()
        print("\n=== DEBATE VERDICT ===")
        print(verdict)
    except Exception as e:
        print(f"Debate failed: {e}")

if __name__ == "__main__":
    main()
