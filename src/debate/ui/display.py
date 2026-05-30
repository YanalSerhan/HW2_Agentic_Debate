"""Terminal UI display components using rich."""
import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def print_header(topic: str, rounds: int):
    """Prints the debate header."""
    from debate.rag.role_assigner import RoleAssigner
    roles = RoleAssigner().assign_roles(topic)
    
    header = Text(f"DEBATE: {topic}", style="bold white on blue", justify="center")
    console.print()
    console.print(Panel(header, title="[bold]Multi-Agent Debate System[/bold]"))
    
    pro_name = "Christopher Hitchens" if roles["pro"] == "hitchens" else "Noam Chomsky"
    con_name = "Christopher Hitchens" if roles["con"] == "hitchens" else "Noam Chomsky"
    
    sides_text = Text(f"{pro_name} (Pro) vs {con_name} (Con)", style="bold yellow", justify="center")
    console.print(sides_text)
    
    console.print(f"[dim]Scheduled for {rounds} rounds[/dim]\n")

def _extract_evidence(msg_content: str) -> tuple[str, str]:
    """Helper to separate main text from evidence block if formatted simply."""
    parts = msg_content.split("\n\nEvidence Used:")
    if len(parts) > 1:
        return parts[0], "Evidence Used:" + parts[1]
    return msg_content, ""

def display_round(round_number: int, pro_msg: str, con_msg: str):
    """Displays a single debate round with formatted panels."""
    console.print(f"\n[bold underline]Round {round_number}[/bold underline]")
    
    # Pro Panel
    pro_text, pro_ev = _extract_evidence(pro_msg)
    p_content = Text(pro_text)
    if pro_ev:
        p_content.append("\n\n" + pro_ev, style="dim")
        
    console.print(Panel(
        p_content, 
        title="[bold blue]Pro Agent[/bold blue]", 
        border_style="blue",
        subtitle=f"Round {round_number}"
    ))
    
    # Con Panel
    con_text, con_ev = _extract_evidence(con_msg)
    c_content = Text(con_text)
    if con_ev:
        c_content.append("\n\n" + con_ev, style="dim")
        
    console.print(Panel(
        c_content, 
        title="[bold red]Con Agent[/bold red]", 
        border_style="red",
        subtitle=f"Round {round_number}"
    ))

def display_verdict(verdict: Any):
    """Displays the final verdict in a styled box."""
    # Ensure it's a Verdict object or similar
    console.print("\n")
    
    # Create scores table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="dim", width=12)
    table.add_column("Score", justify="right")
    
    winner_str = verdict.winner if isinstance(verdict.winner, str) else verdict.winner.name
    
    table.add_row(
        "[blue]Pro[/blue]" if winner_str == "PRO" else "Pro", 
        f"{verdict.pro_score:.1f}"
    )
    table.add_row(
        "[red]Con[/red]" if winner_str == "CON" else "Con", 
        f"{verdict.con_score:.1f}"
    )
    
    reasoning = Text(verdict.reasoning)
    
    key_args = ""
    if verdict.key_winning_arguments:
        key_args = "\n\n[bold]Key Winning Arguments:[/bold]\n" + "\n".join(
            f"- {arg}" for arg in verdict.key_winning_arguments
        )
        
    content = Table.grid(padding=1)
    content.add_column()
    content.add_row(table)
    content.add_row("")
    content.add_row("[bold underline]Judge's Reasoning[/bold underline]")
    content.add_row(reasoning)
    if key_args:
        content.add_row(key_args)
        
    stats = f"Rounds: {verdict.round_count} | Tokens: {verdict.total_tokens_used:,} | Cost: ${verdict.total_cost_usd:.4f}"
    
    panel = Panel(
        content,
        title=f"[bold yellow]FINAL VERDICT: {winner_str} WINS[/bold yellow]",
        border_style="yellow",
        subtitle=stats
    )
    console.print(panel)
    console.print("\n")
