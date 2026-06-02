"""Auto-generated docstring."""

import glob
import os

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

from debate.cli import cost, replay, run, visualize

console = Console()

def display_header():
    """Auto-generated docstring."""
    console.clear()
    console.print(Panel.fit("[bold cyan]Agentic Debate System[/bold cyan]\nHitchens vs Chomsky", border_style="cyan"))

def run_menu():
    """Auto-generated docstring."""
    while True:
        display_header()
        console.print("1. Start a new debate")
        console.print("2. Replay a saved debate")
        console.print("3. Visualize a debate")
        console.print("4. Cost analysis")
        console.print("5. Exit\n")

        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            topic = Prompt.ask("Enter debate topic")
            rounds = IntPrompt.ask("Enter number of rounds (min 3)", default=10)
            try:
                run(topic=topic, rounds=rounds, model=None, log_level="INFO", output_dir="results/", verbose=True)
            except typer.Exit:
                pass
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
            Prompt.ask("\nPress Enter to return to menu")

        elif choice in ["2", "3", "4"]:
            files = sorted(glob.glob("results/*.json"))
            if not files:
                console.print("[yellow]No saved debates found in results/ directory.[/yellow]")
                Prompt.ask("\nPress Enter to return to menu")
                continue

            console.print("\nSaved debates:")
            for i, f in enumerate(files, 1):
                console.print(f"{i}. {os.path.basename(f)}")

            f_choice = IntPrompt.ask("Select a file by number (or 0 to cancel)", default=0)
            if f_choice == 0 or f_choice > len(files):
                continue

            selected_file = files[f_choice - 1]
            try:
                if choice == "2":
                    replay(selected_file)
                elif choice == "3":
                    visualize(selected_file)
                elif choice == "4":
                    cost(selected_file)
            except typer.Exit:
                pass
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

            Prompt.ask("\nPress Enter to return to menu")

        elif choice == "5":
            console.print("[green]Exiting...[/green]")
            break
