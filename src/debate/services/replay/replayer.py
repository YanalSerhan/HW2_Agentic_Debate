"""Debate Replayer module."""
import json
import time

from rich.console import Console

from debate.services.debate.verdict import Verdict
from debate.services.ui.display import display_round, display_verdict, print_header

console = Console()

class DebateReplayer:
    """Replays a saved debate transcript without API calls."""

    def replay(self, transcript_path: str):
        """Re-renders the full debate from a JSON transcript."""
        try:
            with open(transcript_path) as f:
                data = json.load(f)
        except Exception as e:
            console.print(f"[bold red]Failed to load file: {e}[/bold red]")
            return

        topic = data.get("topic", "Unknown")
        rounds = data.get("rounds", [])

        # Display header
        print_header(topic, len(rounds))

        # Display each round
        for rnd in rounds:
            display_round(rnd["round_number"], rnd["pro_message"], rnd["con_message"])
            time.sleep(1) # Small pause for effect

        # Display verdict
        v_data = data.get("verdict", {})
        if v_data:
            display_verdict(Verdict(**v_data))
