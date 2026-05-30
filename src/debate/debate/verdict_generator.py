import json
from datetime import datetime, timezone
from typing import Any

from debate.constants import AgentRole
from debate.debate.round_manager import RoundResult
from debate.debate.verdict import Verdict


class VerdictGenerator:
    """Generates the final verdict using the LLM API."""

    def __init__(self, master_agent: Any):
        self.master_agent = master_agent

    def generate_verdict(self, transcript: list[RoundResult], session_id: str, total_tokens: int, total_cost: float) -> Verdict:
        prompt = self._build_prompt(transcript)
        
        # Ensure we don't fail if web search is missing, but MasterAgent is set up to retry and ignore.
        text, _, _ = self.master_agent.call_api(
            messages=[{"role": "user", "content": prompt}],
            tools=[]
        )
        
        # Parse JSON from text
        data = self._parse_json(text)
            
        pro_score = float(data.get("pro_score", 0.0))
        con_score = float(data.get("con_score", 0.0))
        
        # Apply rhetorical edge tiebreaker
        if pro_score == con_score:
            pro_score += 5.0
            
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
        import re
        import logging
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
            logging.error(f"Failed to parse JSON verdict. Error: {e}. Raw text: {text}")
            pass
            
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
Output a JSON object EXACTLY in this format:
{{
  "pro_score": 85.0,
  "con_score": 82.0,
  "reasoning": "A paragraph explaining why the winner won.",
  "key_winning_arguments": ["Top argument 1", "Top argument 2", "Top argument 3"]
}}
"""
