# API Gatekeeper (PRD_gatekeeper)

### Rate Limit Config Schema
The API Gatekeeper relies on `config/rate_limits.json`.
```json
{
  "requests_per_minute": 30,
  "requests_per_hour": 500,
  "concurrent_max": 3,
  "retry_after_seconds": 30,
  "max_retries": 3,
  "queue_max_depth": 100
}
```

### Queue Behavior
- FIFO (First-In-First-Out) implementation.
- Max queue depth of 100.
- Centralizes all API calls; no API calls bypass the gatekeeper (enforced at the architecture level).

### Retry Policy
- Retries on transient network/API failures.
- Employs exponential backoff: 1s, 2s, 4s.
- Aborts and raises an exception after exhausting `max_retries`.

### Backpressure Signaling
- If the queue exceeds `queue_max_depth`, the Gatekeeper raises a `GatekeeperQueueFullError`.
- This signaling forces the agents/SDK to slow down generation requests.

### Monitoring Hooks
- Emits metrics on each call via `LoggingMixin`.
- Calculates API call timing, prompt tokens, completion tokens, and estimated cost (USD) for every invocation.
