# HW2_Agentic_Debate

## Usage

Generate score timeline and token usage charts for a completed debate:
```bash
uv run python src/main.py visualize --file results/session_id_topic.json
```

Replay a saved debate (renders the transcript nicely in the terminal without using any API tokens):
```bash
uv run python src/main.py replay --file results/session_id_topic.json
```

Check the status of the API Gatekeeper queue:
```bash
uv run python src/main.py status
```