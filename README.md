# Multi-Agent AI Debate System: Hitchens vs Chomsky

A fully autonomous, multi-agent debate framework where highly-opinionated AI personas battle over complex topics, rigorously retrieving web evidence to dismantle each other's arguments, while being judged by Justice Ruth Bader Ginsburg.

---

## What It Does

This system orchestrates a complex, multi-round debate using strict inter-process communication. It assigns roles dynamically to the most fitting debater personas:
- **Christopher Hitchens (Pro/Con):** Aggressive, evidence-demanding, applying "Hitchens's Razor" to demolish unsupported assertions.
- **Noam Chomsky (Pro/Con):** Calm, systemic, exposing hidden institutional assumptions and power dynamics.
- **Justice Ruth Bader Ginsburg (Master Agent):** The impartial judge who actively scores each round using a strict 0-100 rubric on rhetorical strength, evidence quality, logical coherence, and counter-argument effectiveness.

At the end of the debate, Justice Ginsburg delivers a final parsed JSON verdict declaring the winner and the key winning arguments.

## Visualization

The debate produces high-quality visualizations to trace the persuasion shifts over the rounds.

![Score Timeline](assets/score_timeline.png)

![Token Usage](assets/token_usage.png)

![Final Verdict](assets/final_verdict.png)

## Quotes from a Real Debate

> **Hitchens (Con):** *"Your opponent presents a bald assertion without evidence. Let us examine it by the Hitchens Razor itself: What is asserted without evidence may be dismissed without evidence. But I will not dismiss it. I will annihilate it by showing the evidence contradicts him entirely."*

> **Chomsky (Pro):** *"I appreciate the invitation to engage with this question, though I should begin by noting that the framing itself warrants examination... The evidence suggests something more precise: religion is a system of meaning that can be captured and weaponized by power, or it can remain autonomous and critical of power."*

## Quick Start

### Installation

```bash
git clone https://github.com/YanalSerhan/HW2_Agentic_Debate.git
cd HW2_Agentic_Debate
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY
uv sync
```

### Run a Debate

```bash
# Run a lively 5-round debate
uv run python src/main.py run --topic "AI will inevitably destroy humanity" --rounds 5 --verbose
```

### Replay a Debate
If you want to view the stunning terminal UI output of a previously run debate (without incurring API costs!):
```bash
uv run python src/main.py replay --file results/sample_debate.json
```

## Cost Analysis

```text
            Debate Cost Analysis            
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Metric                         ┃   Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Total Input Tokens             │ 132,990 │
│ Total Output Tokens            │  33,247 │
│ Total Tokens                   │ 166,238 │
│ Total Rounds                   │       3 │
│ Cost Per Round                 │ $0.0556 │
│ Cost Per Agent (Approx)        │ $0.0834 │
│ Total Cost (1 Debate)          │ $0.1668 │
├────────────────────────────────┼─────────┤
│ Projected Cost (10 Debates)    │   $1.67 │
│ Projected Cost (100 Debates)   │  $16.68 │
│ Projected Cost (1,000 Debates) │ $166.76 │
└────────────────────────────────┴─────────┘
```

## Prompt Engineering
To see how we evolved our agents from generating basic responses to delivering rich, persona-driven, evidence-backed arguments, check out our [Prompt Engineering Log](prompts/prompt_log.md).