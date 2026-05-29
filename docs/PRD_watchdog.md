# Watchdog System (PRD_watchdog)

### Per-Agent Timeout
- The Watchdog enforces a configurable maximum timeout per agent turn (default is 30s).
- It runs as a background daemon thread that monitors the child process's execution time.

### Keep-Alive Mechanism
- Uses a heartbeat ping/pong mechanism.
- `ping_watchdog()` is called by the agent after each successful round to reset the timer.

### Recovery Behavior
- **Kill and Restart**: If an agent times out, the Watchdog thread forcefully terminates the offending process.
- **Context Re-Injection**: The Watchdog triggers a restart of the process and re-injects the last known context to attempt to resume the debate.
- **Max Restart Attempts**: The system attempts recovery up to a maximum of 2 times. If the process fails on the third attempt, the Watchdog escalates the failure to the Father agent.
- **Forfeit**: Upon escalation, the Father agent logs the catastrophic failure and declares the offending side forfeit.
