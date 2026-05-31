# Multi-Agent AI Debate System: Hitchens vs Chomsky

A fully autonomous, multi-agent debate framework where highly-opinionated AI personas battle over complex topics, rigorously retrieving web evidence to dismantle each other's arguments, while being judged by Justice Ruth Bader Ginsburg.

---

## What It Does

This system orchestrates a complex, multi-round debate using strict inter-process communication. It assigns roles dynamically to the most fitting debater personas:
- **Christopher Hitchens (Pro/Con):** Aggressive, evidence-demanding, applying "Hitchens's Razor" to demolish unsupported assertions.
- **Noam Chomsky (Pro/Con):** Calm, systemic, exposing hidden institutional assumptions and power dynamics.
- **Justice Ruth Bader Ginsburg (Master Agent):** The impartial judge who actively scores each round using a strict 0-100 rubric on rhetorical strength, evidence quality, logical coherence, and counter-argument effectiveness.

At the end of the debate, Justice Ginsburg delivers a final parsed JSON verdict declaring the winner and the key winning arguments.

## 10-Round Showcase Debate: AI's Impact on Humanity

We ran a full 10-round debate to demonstrate the system's capabilities and rigorous evidence standards. **Con won 54.2 to 45.8.**

### Justice Ginsburg's Final Verdict
> *"Con wins because Pro conflates theoretical potential with demonstrated reality. While Pro correctly identifies real productivity gains and wage premiums for AI-skilled workers, Con effectively exposes the logical flaw: these benefits accrue to those already positioned to capture them, while institutions designed to redistribute gains remain unbuilt. Pro's entire case depends on Phase III pharmaceutical trials arriving in 2026 to validate efficacy—yet even if successful, one approval does not prove systematic benefit. Con maintains evidentiary discipline throughout, acknowledging genuine wage and productivity data while demonstrating why their concentration among elite workers undermines Pro's 'humanity' claim. The burden of proof properly rests with Pro to show institutional reform will occur; Pro offers only exhortations that it must."*

### Replay the Showcase (Free & Instant)
You can view the stunning terminal UI output of this 10-round showcase without spending a single API token:
```bash
uv run python src/main.py replay --file results/showcase_10round_debate.json
```
*(Note: The system defaults to 10 rounds per the assignment. Rounds may be reduced to a minimum of 3 only to conserve API budget).*

### Architectural Evidence: Star Topology
The system uses a strict Star Topology over `multiprocessing.Queue`. Children can ONLY speak to the Father. Here is the IPC routing log proof from the showcase:

| Sender | Recipient | Message Count |
|--------|-----------|---------------|
| Father | Con       | 134           |
| Father | Pro       | 121           |
| Con    | Father    | 44            |
| Pro    | Father    | 35            |
| Con    | Pro       | **0 (BLOCKED)** |
| Pro    | Con       | **0 (BLOCKED)** |

### Visualizations

The system produces high-quality dynamic visualizations to trace persuasion shifts and token costs over the 10 rounds:

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

### Interactive Menu

The primary way to use the app is via the interactive terminal menu. Just run `uv run python src/main.py` with no arguments to launch it!

```bash
uv run python src/main.py
```

### Run a Debate via CLI

```bash
# Run a lively debate
uv run python src/main.py run --topic "AI will inevitably destroy humanity" --rounds 10 --verbose
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