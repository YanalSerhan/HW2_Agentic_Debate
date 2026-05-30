"""Cost analysis module."""
import json
import logging
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)

class CostAnalyzer:
    """Analyzes token usage and computes financial costs from a debate transcript."""
    
    def __init__(self):
        self.report = {}
        self.console = Console()

    def analyze(self, transcript_path: str) -> dict:
        """Read a transcript and compute cost metrics."""
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        verdict = data.get("verdict", {})
        total_tokens = data.get("total_tokens", verdict.get("total_tokens_used", 0))
        total_cost = data.get("total_cost_usd", verdict.get("total_cost_usd", 0.0))
        round_count = verdict.get("round_count", len(data.get("rounds", [])))
        
        # Handle missing input/output token split in older transcripts
        total_input_tokens = data.get("total_input_tokens", 0)
        total_output_tokens = data.get("total_output_tokens", 0)
        
        if total_input_tokens == 0 and total_output_tokens == 0 and total_tokens > 0:
            # Approximate split if not tracked explicitly in the JSON
            total_input_tokens = int(total_tokens * 0.8)
            total_output_tokens = int(total_tokens * 0.2)
            
        cost_per_round = total_cost / round_count if round_count > 0 else 0
        cost_per_agent = total_cost / 2 # Approx 2 main agents
        
        self.report = {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "round_count": round_count,
            "cost_per_round": cost_per_round,
            "cost_per_agent": cost_per_agent,
            "total_cost": total_cost,
            "projected_10": total_cost * 10,
            "projected_100": total_cost * 100,
            "projected_1000": total_cost * 1000,
        }
        return self.report

    def print_report(self):
        """Print a rich formatted cost analysis table."""
        if not self.report:
            logger.error("No report generated. Call analyze() first.")
            return

        table = Table(title="Debate Cost Analysis", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")

        r = self.report
        table.add_row("Total Input Tokens", f"{r['total_input_tokens']:,}")
        table.add_row("Total Output Tokens", f"{r['total_output_tokens']:,}")
        table.add_row("Total Tokens", f"{r['total_tokens']:,}")
        table.add_row("Total Rounds", f"{r['round_count']}")
        table.add_row("Cost Per Round", f"${r['cost_per_round']:.4f}")
        table.add_row("Cost Per Agent (Approx)", f"${r['cost_per_agent']:.4f}")
        table.add_row("Total Cost (1 Debate)", f"${r['total_cost']:.4f}")
        table.add_section()
        table.add_row("Projected Cost (10 Debates)", f"${r['projected_10']:.2f}")
        table.add_row("Projected Cost (100 Debates)", f"${r['projected_100']:.2f}")
        table.add_row("Projected Cost (1,000 Debates)", f"${r['projected_1000']:.2f}")

        self.console.print(table)
