"""CLI interface using Typer."""
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from debate.sdk.sdk import DebateSDK
from debate.ui.display import display_round, display_verdict, print_header

app = typer.Typer(help="Multi-Agent AI Debate System CLI")
console = Console()

@app.command()
def run(
    topic: str = typer.Option(..., "--topic", help="The debate topic"),
    rounds: int = typer.Option(10, "--rounds", min=5, help="Number of rounds"),
    model: Optional[str] = typer.Option(None, "--model", help="LLM model to use"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
    output_dir: str = typer.Option("results/", "--output-dir", help="Where to save transcript"),
    verbose: bool = typer.Option(False, "--verbose/--no-verbose", help="Show live debate vs. just verdict"),
):
    """Run a debate on a given topic."""
    
    # Configure root logger
    numeric_level = getattr(logging, log_level.upper(), None)
    if isinstance(numeric_level, int):
        logging.getLogger().setLevel(numeric_level)

    print_header(topic, rounds)

    # Initialize SDK
    sdk = DebateSDK(topic=topic, max_rounds=rounds)
    if model:
        sdk.config_manager.config["model"] = model

    # Set up callback if verbose
    if verbose:
        def on_round(rnd_num: int, pro_msg: str, con_msg: str):
            display_round(rnd_num, pro_msg, con_msg)
        sdk.on_round = on_round
    
    console.print(f"[bold green]Starting debate ({rounds} rounds)...[/bold green]")
    start_time = time.time()
    
    try:
        verdict = sdk.run_debate()
    except Exception as e:
        console.print(f"[bold red]Debate failed: {e}[/bold red]")
        raise typer.Exit(1)
        
    duration = time.time() - start_time
    
    # Display verdict
    display_verdict(verdict)
    
    # Save transcript
    transcript = sdk.get_transcript()
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    topic_slug = re.sub(r'[^a-z0-9]+', '_', topic.lower()).strip('_')
    file_path = out_path / f"{verdict.session_id}_{topic_slug}.json"
    
    data = {
        "session_id": verdict.session_id,
        "topic": topic,
        "started_at": datetime.fromtimestamp(start_time).isoformat(),
        "completed_at": datetime.now().isoformat(),
        "rounds": [r.model_dump(mode="json") for r in transcript],
        "verdict": verdict.model_dump(mode="json"),
        "total_cost_usd": verdict.total_cost_usd,
        "total_tokens": verdict.total_tokens_used,
        "duration_seconds": duration,
    }
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
        
    console.print(f"\n[dim]Transcript saved to: {file_path}[/dim]")

@app.command()
def replay(
    file: str = typer.Option(..., "--file", help="Path to transcript JSON file")
):
    """Replay a saved debate transcript."""
    try:
        with open(file, "r") as f:
            data = json.load(f)
    except Exception as e:
        console.print(f"[bold red]Failed to load file: {e}[/bold red]")
        raise typer.Exit(1)
        
    print_header(data.get("topic", "Unknown"), len(data.get("rounds", [])))
    
    for rnd in data.get("rounds", []):
        display_round(rnd["round_number"], rnd["pro_message"], rnd["con_message"])
        time.sleep(1) # Small pause for effect
        
    # Reconstruct verdict for display
    from debate.debate.verdict import Verdict
    v_data = data.get("verdict", {})
    if v_data:
        display_verdict(Verdict(**v_data))

@app.command()
def status():
    """Show gatekeeper queue status."""
    sdk = DebateSDK(topic="status_check")
    status = sdk.get_queue_status()
    console.print("[bold]Gatekeeper Status:[/bold]")
    console.print(f"Queue Depth: {status.depth} / {status.max_depth}")
    console.print(f"Requests this minute: {status.requests_this_minute}")
    console.print(f"Requests this hour: {status.requests_this_hour}")

def main():
    app()

if __name__ == "__main__":
    main()
