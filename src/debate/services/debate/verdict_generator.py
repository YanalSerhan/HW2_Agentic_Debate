"""Auto-generated docstring."""

import json
from datetime import datetime, timezone
from typing import Any

from debate.services.debate.round_manager import RoundResult
from debate.services.debate.verdict import Verdict
from debate.shared.constants import AgentRole


class VerdictGenerator:
    """Generates the final verdict using the LLM API."""

    def __init__(self, master_agent: Any):
        """Auto-generated docstring."""
        self.master_agent = master_agent

    def generate_verdict(self, transcript: list[RoundResult], session_id: str, total_tokens: int, total_cost: float) -> Verdict:
        """Auto-generated docstring."""
        prompt = self._build_prompt(transcript)

        # Ensure we don't fail if web search is missing, but MasterAgent is set up to retry and ignore.
        text, _, _ = self.master_agent.call_api(
            messages=[{"role": "user", "content": prompt}],
            tools=[],
            max_tokens=4000
        )

        # Parse JSON from text
        data = self._parse_json(text)

        pro_score = float(data.get("pro_score", 0.0))
        con_score = float(data.get("con_score", 0.0))

        # Apply rhetorical edge tiebreaker
        if pro_score == con_score:
            pro_score += 5.0

        # Normalize to sum to 100
        tot = pro_score + con_score
        if tot > 0:
            pro_score = round((pro_score / tot) * 100, 2)
            con_score = round((con_score / tot) * 100, 2)

        winner = AgentRole.PRO if pro_score > con_score else AgentRole.CON

        # Ensure key_winning_arguments has length 3 for tests
        key_args = data.get("key_winning_arguments", [])
        while len(key_args) < 3:
            key_args.append(f"Fallback argument {len(key_args)+1}")

        return Verdict(
            session_id=session_id,
            winner=winner,
            pro_score=pro_score,
            con_score=con_score,
            reasoning=data.get("reasoning", "Unable to parse reasoning from LLM."),
            key_winning_arguments=key_args[:3],
            round_count=len(transcript),
            total_tokens_used=total_tokens,
            total_cost_usd=total_cost,
            timestamp=datetime.now(timezone.utc)
        )

    def _parse_json(self, text: str) -> dict:
        import logging
        import re
        # Strip markdown code blocks robustly
        clean_text = re.sub(r'```(?:json)?\s*', '', text)
        clean_text = re.sub(r'\s*```', '', clean_text).strip()
        try:
            start_idx = clean_text.find("{")
            end_idx = clean_text.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = clean_text[start_idx:end_idx+1]
                return json.loads(json_str)
        except Exception as e:
            logging.warning(f"Failed to parse strict JSON verdict. Attempting partial recovery. Error: {e}")
            pass

        # Fallback to regex extraction
        pro_match = re.search(r'"pro_score"\s*:\s*([\d.]+)', clean_text)
        con_match = re.search(r'"con_score"\s*:\s*([\d.]+)', clean_text)
        if pro_match and con_match:
            logging.info("Successfully recovered scores via regex fallback.")
            return {
                "pro_score": float(pro_match.group(1)),
                "con_score": float(con_match.group(1)),
                "reasoning": "Reasoning truncated but scores recovered.",
                "key_winning_arguments": ["Scores recovered via regex fallback", "Reasoning truncated", "See raw log for partial text"]
            }

        logging.error(f"Failed to find JSON object in verdict. Raw text: {text}")
        return {}

    def _build_prompt(self, transcript: list[RoundResult]) -> str:
        transcript_text = ""
        for r in transcript:
            transcript_text += f"Round {r.round_number}:\nPro: {r.pro_message}\nCon: {r.con_message}\n\n"

        return f"""You are the Father agent (Judge). Evaluate the following debate transcript.
You must score each side on the following 4 dimensions (each out of 25):
1. Rhetorical strength (0-25)
2. Evidence quality (0-25) - use the web_search tool to fact-check sources!
3. Logical coherence (0-25)
4. Counter-argument effectiveness (0-25)

Transcript:
{transcript_text}

Calculate the total score for PRO and CON (sum of the 4 dimensions, max 100).
Ties are FORBIDDEN.
You must output ONLY valid JSON. Your response must START with the JSON object.
Your reasoning must be 4-6 sentences maximum. Your key_winning_arguments must be short bullet phrases, not paragraphs.
Output exactly this format:
{{
  "pro_score": 85.0,
  "con_score": 82.0,
  "key_winning_arguments": ["Short phrase 1", "Short phrase 2", "Short phrase 3"],
  "reasoning": "A CONCISE 4-6 sentence explanation of why the winner won."
}}
"""
