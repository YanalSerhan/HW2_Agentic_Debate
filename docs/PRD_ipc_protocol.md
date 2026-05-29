# IPC Protocol Specifications (PRD_ipc_protocol)

### Message Types
- `ARGUMENT`: An initial claim or argument presented by the Pro agent.
- `COUNTER_ARGUMENT`: A direct response and rebuttal by the Con agent.
- `SEARCH_RESULT`: Encapsulates web search context derived by an agent.
- `VERDICT_REQUEST`: A signal from the MasterAgent indicating the debate has concluded and a verdict is pending.
- `VERDICT`: The final output message from the Father judge detailing the outcome.
- `PING`: Keep-alive message used by Watchdog.
- `PONG`: Keep-alive response used by Watchdog.
- `ERROR`: An encapsulation of any runtime, validation, or network error.

### JSON Schemas
All messages are serialized/deserialized using Pydantic. Base schema representation:

```json
{
  "message_id": "uuid-string",
  "session_id": "uuid-string",
  "sender": "PRO|CON|FATHER",
  "recipient": "PRO|CON|FATHER",
  "message_type": "ARGUMENT|COUNTER_ARGUMENT|VERDICT|...",
  "round_number": 1,
  "content": "Text content of the message",
  "evidence": [
    {
      "url": "https://example.com",
      "title": "Page Title",
      "snippet": "Relevant text...",
      "retrieved_at": "ISO8601-timestamp"
    }
  ],
  "timestamp": "ISO8601-timestamp",
  "metadata": {}
}
```

### Routing Rules
- All communication must flow through the Father (MasterAgent).
- Child 1 (Pro) sends to Father. Father forwards to Child 2 (Con).
- Child 2 (Con) sends to Father. Father forwards to Child 1 (Pro).
- Direct sibling messaging (Pro -> Con or Con -> Pro) is strictly prohibited and must raise a validation error.

### Error and Timeout Handling
- `IPCTimeoutError` is raised if a `receive()` operation exceeds the configured timeout (default 30.0s).
- `IPCQueueFullError` is raised if a `send()` operation targets a full queue.
- Malformed JSON messages do not crash the process; instead, they are converted into `ERROR` message types and logged.

### Queue Management
- Utilizes `multiprocessing.Queue`.
- Operates on a strict First-In-First-Out (FIFO) basis.
- Enforces a maximum depth to apply backpressure.
