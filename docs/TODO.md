# TODO.md — Multi-Agent AI Debate System
## Professional Engineering Execution Plan

> **Project:** Exercise 02 — AI Agent Debate System  
> **Course:** Agents, Subagents, Commands and Skills (Lesson 05)  
> **Instructor:** Dr. Yoram Segal  
> **Architecture:** Master Agent (Judge) orchestrating two specialized Subagents (Pro/Con) via Python IPC  
> **Version:** 1.00  
> **Status:** Planning Phase

---

## Table of Contents

1. [Project Overview & Architecture Summary](#1-project-overview--architecture-summary)
2. [Phase 0: Planning & Documentation](#phase-0-planning--documentation)
3. [Phase 1: Project Skeleton & Infrastructure](#phase-1-project-skeleton--infrastructure)
4. [Phase 2: Core SDK & Gatekeeper Layer](#phase-2-core-sdk--gatekeeper-layer)
5. [Phase 3: Agent Implementation](#phase-3-agent-implementation)
6. [Phase 4: IPC Communication & Orchestration](#phase-4-ipc-communication--orchestration)
7. [Phase 5: Debate Logic & Round Management](#phase-5-debate-logic--round-management)
8. [Phase 6: Judging System](#phase-6-judging-system)
9. [Phase 7: CLI Interface](#phase-7-cli-interface)
10. [Phase 8: Logging, Monitoring & Observability](#phase-8-logging-monitoring--observability)
11. [Phase 9: Testing Suite](#phase-9-testing-suite)
12. [Phase 10: Configuration, Security & Hardening](#phase-10-configuration-security--hardening)
13. [Phase 11: Research, Analysis & Visualization](#phase-11-research-analysis--visualization)
14. [Phase 12: Documentation & Submission](#phase-12-documentation--submission)
15. [Quality Gates & Phase Completion Checklist](#quality-gates--phase-completion-checklist)
16. [Nice-to-Have Improvements](#nice-to-have-improvements)
17. [Creative / Advanced Features](#creative--advanced-features)

---

## 1. Project Overview & Architecture Summary

### System Description
A three-agent debate system implemented in Python where:
- **Father/Judge Agent** (`MasterAgent`): Orchestrates the debate, evaluates arguments by persuasive power (not factual correctness), and delivers a final verdict with reasoning.
- **Pro Agent** (`ProSubagent`): Champions one side of a given debate topic. Has its own unique Skill set that differs from the Con agent.
- **Con Agent** (`ConSubagent`): Champions the opposing side. Must never agree with the Pro agent automatically.
- Communication flows exclusively through the Father: `Child → Father → Child` (no direct sibling communication).
- All agents are separate Python **processes** communicating via IPC (Inter-Process Communication).
- Web search is a **mandatory tool** (`tool_use`) used in every agent's reasoning.
- All agent-to-agent communication is serialized in **JSON** format.
- The debate requires a minimum of **10 pings** (argument/counter-argument pairs).
- Each agent has a dedicated `Skill` (`.skill.md` + Python implementation) distinct from its counterpart.
- All API calls route through a centralized **Gatekeeper** with rate limiting and queue management.

### Mandatory Constraints (from assignment)
- [ ] Two-child debate with a Father judge — no direct sibling IPC
- [ ] Minimum 10 pings per agent side (10 arguments + 10 counter-arguments)
- [ ] Each agent must have a unique `Skill` (distinct prompt + implementation)
- [ ] Web search (`tool_use`) is mandatory — hardcoded verification required
- [ ] JSON communication format throughout
- [ ] No LLM calls directly from `subprocess`/shell — only Python orchestration
- [ ] No politically correct/sanitized debate style (authentic argumentation)
- [ ] Father evaluates by **persuasion power**, not factual truth
- [ ] Timeouts on all agent calls (Watchdog pattern)
- [ ] OOP architecture with inheritance and mixins
- [ ] No code duplication — shared logic in base classes
- [ ] All config externalized — zero hardcoded values
- [ ] `uv` as the only package manager
- [ ] `ruff` linting with zero violations
- [ ] TDD: tests written before/alongside code
- [ ] Minimum 85% test coverage
- [ ] All files ≤ 150 lines of code
- [ ] Structured logs (JSONL format), rotating at 20 files × 500 lines
- [ ] `README.md`, `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` are mandatory

---

## Phase 0: Planning & Documentation

**Goal:** Establish all planning documents before writing any code. This phase must be completed and reviewed before Phase 1 begins.

**Completion criteria:** All four documents exist, are reviewed, and represent a coherent plan.

### 0.1 — Create `docs/PRD.md`

- [x] Write project overview: purpose, context, academic constraints
- [x] Define stakeholder goals: student submission + AI grader evaluation
- [x] Define user stories:
  - As a user, I can specify a debate topic via CLI and receive a verdict
  - As a user, I can observe the full debate transcript in real time
  - As a user, I can adjust the number of debate rounds (down to 5 if budget-limited)
  - As a user, I can review structured logs of all agent interactions
- [x] Define functional requirements:
  - Three-process architecture (Father + Pro + Con)
  - Minimum 10 exchange rounds per agent
  - Mandatory web search tool integration
  - JSON-serialized IPC messages
  - Father-mediated communication only
  - Unique skills per agent
  - Verdict with explicit scoring rationale
- [x] Define non-functional requirements:
  - Response timeout ≤ 30 seconds per agent turn
  - Graceful degradation if one agent times out
  - Structured JSONL logging
  - Zero hardcoded secrets or values
  - 85%+ test coverage
  - Ruff compliance (zero violations)
- [x] Define out-of-scope items:
  - GUI (terminal-only per assignment)
  - Persistent debate history across sessions
  - Multi-topic simultaneous debates (extension only)
- [x] Define acceptance criteria with KPIs:
  - Debate completes with ≥ 10 rounds
  - Verdict delivered with numeric persuasion score per agent
  - All IPC messages validate against JSON schema
  - All tests pass; coverage ≥ 85%
- [x] Define assumptions and dependencies:
  - Anthropic API key available in environment
  - `uv` installed
  - Python 3.10+
- [x] Sign-off checkpoint: review PRD before proceeding

### 0.2 — Create `docs/PLAN.md`

- [x] Draw C4 Context diagram: User → CLI → MasterAgent → [ProSubagent, ConSubagent] → Anthropic API
- [x] Draw C4 Container diagram: showing three OS processes and IPC channels
- [x] Draw C4 Component diagram: SDK layer, Gatekeeper, Agent base class, Skill system, Router-Skill, Logger
- [x] Document UML class hierarchy:
  - `BaseAgent` (abstract)
    - `MasterAgent(BaseAgent)` — judge role
    - `BaseSubagent(BaseAgent)` — abstract child
      - `ProSubagent(BaseSubagent)`
      - `ConSubagent(BaseSubagent)`
  - `ApiGatekeeper`
  - `DebateSDK` (single entry point)
  - `DebateSession`
  - `RoundResult`
  - `Verdict`
  - `SkillBase` (abstract)
    - `ProSkill(SkillBase)`
    - `ConSkill(SkillBase)`
  - `RouterSkill`
  - `WatchdogMixin`
  - `LoggingMixin`
  - `IPCMixin`
- [x] Document IPC protocol design (JSON schema for each message type)
- [x] Document ADRs (Architectural Decision Records):
  - ADR-001: Why separate OS processes (true IPC, not threads)
  - ADR-002: Why FIFO/Queue for IPC (vs Sockets, Signals)
  - ADR-003: Why Father-mediated communication (assignment requirement + cleaner orchestration)
  - ADR-004: Why JSONL for logs (append-safe, one error doesn't corrupt file)
  - ADR-005: Why `uv` over `pip` (faster, deterministic lockfile)
  - ADR-006: Why TDD with 85% coverage (quality gate, maintainability)
- [x] Document API interface (DebateSDK public methods)
- [x] Document data schemas: DebateMessage, RoundResult, Verdict, LogEntry
- [x] Sign-off checkpoint before proceeding

### 0.3 — Create `docs/TODO.md`

- [x] This file — already complete (self-referential)

### 0.4 — Create Per-Algorithm PRDs

- [x] `docs/PRD_ipc_protocol.md`:
  - Message types: ARGUMENT, COUNTER_ARGUMENT, SEARCH_RESULT, VERDICT_REQUEST, VERDICT, PING, PONG, ERROR
  - Schema for each message type (JSON)
  - Routing rules (child → father → child)
  - Error/timeout handling per message
  - Queue management (FIFO, max depth, backpressure)

- [x] `docs/PRD_judging_algorithm.md`:
  - Input: full transcript of all rounds
  - Scoring dimensions: rhetorical strength, evidence quality (from web search), logical coherence, counter-argument effectiveness
  - Output: per-agent score (0–100), winner declaration, reasoning paragraph
  - Edge case: tie-breaking procedure (mandatory — ties are never allowed)
  - Constraints: judge evaluates persuasion, not truth

- [x] `docs/PRD_skill_system.md`:
  - Skill discovery mechanism (description-based routing)
  - ProSkill behavior: offensive argumentation, evidence-first approach
  - ConSkill behavior: Socratic questioning + rebuttal focus
  - RouterSkill: loads system prompt once, reads opening statement, selects relevant skills, loads only those into context
  - Skill file format: `.skill.md` + companion `.py`

- [x] `docs/PRD_gatekeeper.md`:
  - Rate limit config schema
  - Queue behavior (FIFO, max depth 100)
  - Retry policy (3 retries, exponential backoff)
  - Backpressure signaling
  - Monitoring hooks (emit metrics on each call)

- [x] `docs/PRD_watchdog.md`:
  - Per-agent timeout (configurable, default 30s)
  - Keep-alive mechanism (ping/pong)
  - Recovery behavior: kill + restart process, re-inject context
  - Max restart attempts before escalation to Father

### 0.5 — Architecture Diagram File

- [x] Create `docs/architecture.md` with ASCII diagrams for:
  - Process topology
  - IPC message flow
  - Skill activation flow
  - Gatekeeper flow
  - Watchdog lifecycle

---

## Phase 1: Project Skeleton & Infrastructure

**Goal:** Establish the full project structure and tooling before writing any logic.

**Completion criteria:** `uv sync` works cleanly; `ruff check` returns zero violations on skeleton; `pytest` finds and runs (empty) test suite.

**Dependencies:** Phase 0 must be complete.

### 1.1 — Directory Structure

Create the following structure exactly:

```
debate-agents/
├── src/
│   └── debate/
│       ├── __init__.py
│       ├── sdk/
│       │   └── sdk.py                    # DebateSDK — single entry point
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base_agent.py             # Abstract BaseAgent
│       │   ├── master_agent.py           # Father/Judge
│       │   ├── base_subagent.py          # Abstract BaseSubagent
│       │   ├── pro_subagent.py           # Pro position agent
│       │   └── con_subagent.py           # Con position agent
│       ├── skills/
│       │   ├── __init__.py
│       │   ├── skill_base.py             # Abstract SkillBase
│       │   ├── pro_skill.py              # Pro agent skill
│       │   ├── con_skill.py              # Con agent skill
│       │   ├── router_skill.py           # RouterSkill
│       │   ├── pro_skill.skill.md        # Pro skill prompt
│       │   ├── con_skill.skill.md        # Con skill prompt
│       │   └── router_skill.skill.md     # Router skill prompt
│       ├── ipc/
│       │   ├── __init__.py
│       │   ├── message.py                # DebateMessage dataclass + schema
│       │   ├── ipc_channel.py            # FIFO/Queue abstraction
│       │   └── ipc_mixin.py              # IPCMixin
│       ├── debate/
│       │   ├── __init__.py
│       │   ├── session.py                # DebateSession orchestrator
│       │   ├── round_manager.py          # Round tracking + ping counting
│       │   └── verdict.py                # Verdict dataclass
│       ├── shared/
│       │   ├── __init__.py
│       │   ├── gatekeeper.py             # ApiGatekeeper
│       │   ├── config.py                 # ConfigManager
│       │   ├── version.py                # Version tracking (1.00)
│       │   ├── watchdog.py               # WatchdogMixin
│       │   └── logging_mixin.py          # LoggingMixin
│       └── constants.py                  # Immutable project constants
├── tests/
│   ├── __init__.py
│   ├── conftest.py                       # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_agents/
│   │   │   ├── test_base_agent.py
│   │   │   ├── test_master_agent.py
│   │   │   ├── test_pro_subagent.py
│   │   │   └── test_con_subagent.py
│   │   ├── test_ipc/
│   │   │   ├── test_message.py
│   │   │   └── test_ipc_channel.py
│   │   ├── test_debate/
│   │   │   ├── test_session.py
│   │   │   ├── test_round_manager.py
│   │   │   └── test_verdict.py
│   │   ├── test_skills/
│   │   │   ├── test_skill_base.py
│   │   │   ├── test_pro_skill.py
│   │   │   ├── test_con_skill.py
│   │   │   └── test_router_skill.py
│   │   └── test_shared/
│   │       ├── test_gatekeeper.py
│   │       ├── test_config.py
│   │       ├── test_watchdog.py
│   │       └── test_logging_mixin.py
│   └── integration/
│       ├── __init__.py
│       ├── test_full_debate.py           # End-to-end debate (mocked API)
│       ├── test_ipc_flow.py              # IPC round-trip
│       └── test_gatekeeper_queue.py      # Rate limiting under load
├── config/
│   ├── setup.json                        # Main app config
│   ├── rate_limits.json                  # API rate limit config
│   └── logging_config.json              # Logging configuration
├── docs/
│   ├── PRD.md
│   ├── PLAN.md
│   ├── TODO.md
│   ├── PRD_ipc_protocol.md
│   ├── PRD_judging_algorithm.md
│   ├── PRD_skill_system.md
│   ├── PRD_gatekeeper.md
│   ├── PRD_watchdog.md
│   └── architecture.md
├── logs/                                 # Runtime log directory (git-ignored)
├── results/                              # Debate transcripts + analysis
├── assets/                               # Screenshots, diagrams
├── notebooks/                            # Analysis notebooks
├── prompts/                              # Prompt engineering log
│   └── prompt_log.md
├── src/main.py                           # Entry point (imports SDK, runs CLI)
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
└── .gitignore
```

- [x] Create all directories with `__init__.py` files
- [x] Create all placeholder `.py` files with module docstrings
- [x] Verify directory tree matches spec above

### 1.2 — `pyproject.toml` Configuration

- [x] Set `[project]` metadata: name, version (1.00), description, authors, requires-python = ">=3.10"
- [x] Set `[project.dependencies]`:
  - `anthropic>=0.49.0`
  - `python-dotenv>=1.0.0`
  - `pydantic>=2.0.0` (for JSON schema validation)
  - `rich>=13.0.0` (for terminal output)
  - `typer>=0.12.0` (for CLI)
- [x] Set `[project.optional-dependencies]`:
  - `dev = ["pytest>=8.0", "pytest-cov>=5.0", "pytest-asyncio>=0.23", "ruff>=0.4.0", "pytest-mock>=3.14"]`
- [x] Set `[project.scripts]`: `debate = "debate.sdk.sdk:main"`
- [x] Configure `[tool.ruff]`:
  ```toml
  [tool.ruff]
  line-length = 100
  target-version = "py310"
  [tool.ruff.lint]
  select = ["E","F","W","I","N","UP","B","C4","SIM"]
  ignore = ["E501"]
  ```
- [x] Configure `[tool.pytest.ini_options]`:
  - `testpaths = ["tests"]`
  - `asyncio_mode = "auto"`
- [x] Configure `[tool.coverage.run]`:
  - `source = ["src"]`
  - `omit = ["src/main.py", "*/tests/*"]`
- [x] Configure `[tool.coverage.report]`:
  - `fail_under = 85`
- [x] Run `uv sync` and verify clean install

### 1.3 — `.gitignore`

- [x] Add: `.env`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, `dist/`, `.coverage`, `htmlcov/`, `logs/`, `results/*.json`, `.venv/`, `uv.lock` (do NOT git-ignore lock file — it must be committed)
- [x] **Correction**: keep `uv.lock` tracked (it's a deterministic lockfile, not a secret)
- [x] Add `logs/` to `.gitignore` (runtime artifacts)

### 1.4 — `.env.example`

- [x] Create with placeholder values:
  ```
  ANTHROPIC_API_KEY=your_api_key_here
  DEBATE_MODEL=claude-sonnet-4-20250514
  DEBATE_LOG_LEVEL=INFO
  DEBATE_MAX_ROUNDS=10
  DEBATE_TIMEOUT_SECONDS=30
  ```
- [x] Confirm `.env` is in `.gitignore` and never committed

### 1.5 — `src/debate/shared/version.py`

- [x] Define `VERSION = "1.00"`
- [x] Define `get_version() -> str` function
- [x] Write test: `test_version_format` (matches `\d+\.\d+`)

### 1.6 — `src/debate/constants.py`

- [x] Define all immutable constants using `Enum` where appropriate:
  - `AgentRole(Enum)`: FATHER, PRO, CON
  - `MessageType(Enum)`: ARGUMENT, COUNTER_ARGUMENT, SEARCH_RESULT, VERDICT_REQUEST, VERDICT, PING, PONG, ERROR
  - `DebateStatus(Enum)`: PENDING, IN_PROGRESS, JUDGING, COMPLETE, FAILED
  - `MIN_ROUNDS = 10`
  - `MAX_FILE_LINES = 500`
  - `MAX_LOG_FILES = 20`
- [x] Zero hardcoded strings elsewhere — import from here

---

## Phase 2: Core SDK & Gatekeeper Layer

**Goal:** Build the foundational infrastructure layer that all agents depend on.

**Completion criteria:** `ApiGatekeeper` passes all unit tests; `ConfigManager` loads from JSON; SDK instantiates cleanly.

**Dependencies:** Phase 1 complete.

### 2.1 — `src/debate/shared/config.py` — ConfigManager

- [x] `ConfigManager` class:
  - Loads `config/setup.json`, `config/rate_limits.json`, `config/logging_config.json` on init
  - Validates config version field matches expected version
  - Provides `get(key: str, default=None)` method
  - Provides `get_rate_limit_config() -> RateLimitConfig`
  - Provides `get_logging_config() -> LoggingConfig`
  - Validates required keys on startup; raises `ConfigurationError` if missing
  - File ≤ 150 lines
- [x] `config/setup.json`:
  ```json
  {
    "version": "1.00",
    "model": "claude-sonnet-4-20250514",
    "max_rounds": 10,
    "timeout_seconds": 30,
    "debate_language": "english",
    "min_argument_words": 50,
    "max_argument_words": 300
  }
  ```
- [x] `config/rate_limits.json`:
  ```json
  {
    "rate_limits": {
      "version": "1.00",
      "services": {
        "default": {
          "requests_per_minute": 30,
          "requests_per_hour": 500,
          "concurrent_max": 3,
          "retry_after_seconds": 30,
          "max_retries": 3,
          "queue_max_depth": 100
        }
      }
    }
  }
  ```
- [x] `config/logging_config.json`:
  ```json
  {
    "version": "1.00",
    "log_level": "INFO",
    "log_dir": "logs",
    "max_files": 20,
    "max_lines_per_file": 500,
    "format": "jsonl"
  }
  ```
- [x] Write unit tests:
  - `test_loads_all_config_files`
  - `test_get_returns_default_on_missing_key`
  - `test_raises_on_missing_required_key`
  - `test_version_validated_on_load`

### 2.2 — `src/debate/shared/gatekeeper.py` — ApiGatekeeper

- [x] `RateLimitConfig` dataclass (loaded from `config/rate_limits.json`):
  - `requests_per_minute: int`
  - `requests_per_hour: int`
  - `concurrent_max: int`
  - `retry_after_seconds: int`
  - `max_retries: int`
  - `queue_max_depth: int`
- [x] `QueueStatus` dataclass:
  - `depth: int`
  - `max_depth: int`
  - `requests_this_minute: int`
  - `requests_this_hour: int`
- [x] `ApiGatekeeper` class:
  - `__init__(self, config: RateLimitConfig)`: initializes FIFO queue, counters, sliding window
  - `execute(self, api_call: Callable, *args, **kwargs) -> Any`:
    - Checks rate limits before execution
    - Queues request if limit reached (FIFO)
    - Implements backpressure: raises `GatekeeperQueueFullError` if queue exceeds `queue_max_depth`
    - Retries on transient failures (exponential backoff: 1s, 2s, 4s)
    - Logs all calls with timing in JSONL format
    - Returns result or raises after `max_retries` exhausted
  - `get_queue_status(self) -> QueueStatus`
  - `_check_rate_limit(self) -> bool`: sliding window algorithm
  - `_process_queue(self)`: drains queue when window resets
  - File ≤ 150 lines (split queue logic into `_queue_processor.py` if needed)
- [x] No API calls bypass the gatekeeper — enforce at architecture level
- [x] Write unit tests (mock the actual API call):
  - `test_execute_calls_api_function`
  - `test_rate_limit_enforced`
  - `test_queue_fills_and_backpressure_triggered`
  - `test_retries_on_transient_error`
  - `test_raises_after_max_retries`
  - `test_queue_status_accurate`
  - `test_drains_queue_after_window_reset`

### 2.3 — `src/debate/sdk/sdk.py` — DebateSDK

- [x] `DebateSDK` class (single entry point for all external consumers):
  - `__init__(self, topic: str, config_path: str = "config/")`: loads config, initializes gatekeeper, creates session
  - `run_debate(self) -> Verdict`: orchestrates full debate, returns structured verdict
  - `get_transcript(self) -> list[RoundResult]`: returns all debate rounds
  - `get_queue_status(self) -> QueueStatus`: delegates to gatekeeper
  - All business logic accessed through this class — no direct imports of agent internals from CLI
  - File ≤ 150 lines
- [x] Expose `main()` function for CLI entrypoint
- [x] Write unit tests:
  - `test_sdk_initializes_with_valid_topic`
  - `test_run_debate_returns_verdict` (mocked agents)
  - `test_get_transcript_returns_rounds`

---

## Phase 3: Agent Implementation

**Goal:** Build the three-agent hierarchy with proper OOP design.

**Completion criteria:** All three agent classes instantiate; `BaseAgent` unit tests pass; agents respond to mocked API calls.

**Dependencies:** Phase 2 complete.

### 3.1 — `src/debate/shared/logging_mixin.py` — LoggingMixin

- [x] `LoggingMixin` class:
  - `setup_logging(self, agent_name: str, config: LoggingConfig)`: configures JSONL file logger with rotation
  - `log_event(self, event_type: str, data: dict)`: writes structured JSONL log entry
  - `log_api_call(self, prompt_tokens: int, completion_tokens: int, cost_usd: float)`: dedicated API cost log
  - `log_error(self, error: Exception, context: dict)`: logs error with stack trace
  - Log entry schema:
    ```json
    {
      "timestamp": "ISO8601",
      "agent": "pro|con|father",
      "event_type": "API_CALL|ARGUMENT|VERDICT|ERROR|IPC_SEND|IPC_RECV",
      "session_id": "uuid",
      "round": 3,
      "data": {}
    }
    ```
  - Rotating handler: max 20 files × 500 lines each (JSONL, one record per line)
  - File ≤ 150 lines
- [x] Write unit tests:
  - `test_log_entry_is_valid_json`
  - `test_rotation_triggered_at_500_lines`
  - `test_log_file_created_in_log_dir`

### 3.2 — `src/debate/shared/watchdog.py` — WatchdogMixin

- [x] `WatchdogMixin` class:
  - `start_watchdog(self, timeout: float, process: subprocess.Popen)`: starts background daemon thread monitoring process
  - `ping_watchdog(self)`: resets watchdog timer (called after each successful round)
  - `stop_watchdog(self)`: cleanly stops watchdog thread
  - `_watchdog_loop(self)`: kills process if timeout exceeded, logs kill event, triggers restart callback
  - `on_watchdog_kill(self)`: override in subclass for custom behavior
  - Context manager support (`__enter__`, `__exit__`)
  - File ≤ 150 lines
- [x] Write unit tests:
  - `test_watchdog_kills_process_on_timeout`
  - `test_watchdog_reset_prevents_kill`
  - `test_watchdog_cleans_up_on_stop`
  - `test_context_manager_stops_watchdog`

### 3.3 — `src/debate/ipc/message.py` — DebateMessage

- [x] `DebateMessage` dataclass (Pydantic BaseModel for validation):
  ```python
  class DebateMessage(BaseModel):
      message_id: str          # UUID
      session_id: str          # UUID
      sender: AgentRole
      recipient: AgentRole
      message_type: MessageType
      round_number: int
      content: str
      evidence: list[Evidence]  # web search results used
      timestamp: datetime
      metadata: dict
  ```
- [x] `Evidence` dataclass:
  ```python
  class Evidence(BaseModel):
      url: str
      title: str
      snippet: str
      retrieved_at: datetime
  ```
- [x] `to_json(self) -> str`: serialize to JSON
- [x] `from_json(cls, data: str) -> DebateMessage`: deserialize with validation
- [x] `validate_web_search_used(self) -> bool`: returns `True` if evidence list is non-empty (enforces mandatory search)
- [x] Write unit tests:
  - `test_serialize_deserialize_round_trip`
  - `test_validation_fails_on_invalid_role`
  - `test_validate_web_search_used_requires_evidence`
  - `test_from_json_raises_on_malformed_input`
  - Edge case: `test_empty_evidence_list_serializes_correctly`

### 3.4 — `src/debate/ipc/ipc_channel.py` — IPCChannel

- [x] `IPCChannel` class using `multiprocessing.Queue`:
  - `send(self, message: DebateMessage)`: serializes and puts to queue
  - `receive(self, timeout: float = 30.0) -> DebateMessage`: gets from queue with timeout
  - `is_empty(self) -> bool`
  - `get_depth(self) -> int`
  - Raises `IPCTimeoutError` on receive timeout
  - Raises `IPCQueueFullError` on send to full queue
  - All messages validated on receive (Pydantic)
  - File ≤ 150 lines
- [x] Write unit tests:
  - `test_send_receive_round_trip`
  - `test_receive_raises_on_timeout`
  - `test_queue_full_raises_backpressure_error`
  - `test_message_validated_on_receive`

### 3.5 — `src/debate/ipc/ipc_mixin.py` — IPCMixin

- [x] `IPCMixin`:
  - `send_to_father(self, message: DebateMessage)`: wraps IPCChannel.send
  - `send_to_child(self, agent_role: AgentRole, message: DebateMessage)`: for Father only
  - `receive_message(self, timeout: float) -> DebateMessage`
  - Logs every send/receive event via LoggingMixin
  - Validates sender/recipient routing (child cannot send directly to sibling)

### 3.6 — `src/debate/agents/base_agent.py` — BaseAgent

- [x] Abstract `BaseAgent(LoggingMixin, WatchdogMixin, IPCMixin)`:
  - Abstract methods: `process_message(self, message: DebateMessage) -> DebateMessage`, `get_system_prompt(self) -> str`
  - Concrete methods: `initialize(self, config: ConfigManager)`, `call_api(self, messages: list, tools: list) -> str`
  - `call_api` MUST route through `ApiGatekeeper.execute()`
  - `call_api` MUST include web_search tool in every call
  - `call_api` MUST verify response contains `Evidence` (raises `WebSearchNotUsedError` if absent)
  - `get_role(self) -> AgentRole`
  - `get_session_id(self) -> str`
  - File ≤ 150 lines
- [x] Write unit tests:
  - `test_call_api_routes_through_gatekeeper`
  - `test_call_api_raises_if_no_evidence_in_response`
  - `test_abstract_methods_enforced`

### 3.7 — `src/debate/agents/base_subagent.py` — BaseSubagent

- [x] Abstract `BaseSubagent(BaseAgent)`:
  - `position: str` — the specific stance this agent defends (e.g., "Madrid is better than Barcelona")
  - `get_skill(self) -> SkillBase`: returns agent's unique skill instance
  - `generate_argument(self, round_number: int, history: list[DebateMessage]) -> DebateMessage`
  - `generate_counter_argument(self, opponent_message: DebateMessage, round_number: int) -> DebateMessage`
  - `_build_argument_prompt(self, round_number: int, history: list) -> str`: private
  - MUST call web search tool in every argument generation
  - MUST never agree with the opponent (validated post-generation)
  - File ≤ 150 lines

### 3.8 — `src/debate/agents/pro_subagent.py` — ProSubagent

- [x] `ProSubagent(BaseSubagent)`:
  - `get_system_prompt(self) -> str`: loads `pro_skill.skill.md`, injects position
  - `process_message(self, message: DebateMessage) -> DebateMessage`
  - Pro argumentation style: evidence-first, assertive, factual precedence
  - Unique `ProSkill` strategy: finds and leads with strongest statistical evidence
  - File ≤ 150 lines

### 3.9 — `src/debate/agents/con_subagent.py` — ConSubagent

- [x] `ConSubagent(BaseSubagent)`:
  - `get_system_prompt(self) -> str`: loads `con_skill.skill.md`, injects position
  - `process_message(self, message: DebateMessage) -> DebateMessage`
  - Con argumentation style: Socratic questioning + rebuttal focus, exposes gaps
  - Unique `ConSkill` strategy: identifies weakest link in opponent's evidence chain and attacks it
  - MUST differ significantly from ProSkill (verified in `skill_base.py`)
  - File ≤ 150 lines

### 3.10 — `src/debate/agents/master_agent.py` — MasterAgent

- [x] `MasterAgent(BaseAgent)`:
  - `orchestrate_round(self, round_number: int) -> RoundResult`: requests argument from Pro, sends to Con, receives counter, logs round
  - `request_argument(self, agent: BaseSubagent, context: list) -> DebateMessage`
  - `deliver_to_opponent(self, message: DebateMessage, recipient: BaseSubagent) -> DebateMessage`
  - `deliver_verdict(self, transcript: list[RoundResult]) -> Verdict`
  - `_score_persuasion(self, messages: list[DebateMessage]) -> dict[AgentRole, float]`: calls API with full transcript, returns scores
  - Father NEVER reveals internal state to children
  - Father routes ALL inter-child messages — zero direct sibling IPC
  - File ≤ 150 lines

---

## Phase 4: IPC Communication & Orchestration

**Goal:** Establish working IPC between the three processes.

**Completion criteria:** Integration test `test_ipc_flow.py` passes — messages round-trip cleanly between Father and both children.

**Dependencies:** Phase 3 complete.

### 4.1 — Process Launch Architecture

- [x] `src/debate/debate/session.py` — DebateSession:
  - Launches `ProSubagent` and `ConSubagent` as separate OS processes using `multiprocessing.Process`
  - Creates two `IPCChannel` instances: `father_to_pro`, `father_to_con`
  - Passes channel references to child processes on spawn
  - Maintains process handles for Watchdog
  - Manages process lifecycle: start, monitor, terminate
  - File ≤ 150 lines

- [x] `src/debate/debate/round_manager.py` — RoundManager:
  - `RoundResult` dataclass: `round_number`, `pro_message`, `con_message`, `timestamp`
  - `RoundManager`: tracks round count, validates minimum rounds reached, stores history
  - `increment_round(self) -> int`
  - `get_transcript(self) -> list[RoundResult]`
  - `has_minimum_rounds(self) -> bool` (checks ≥ `MIN_ROUNDS`)
  - File ≤ 150 lines

- [x] `src/debate/debate/verdict.py` — Verdict:
  ```python
  class Verdict(BaseModel):
      session_id: str
      winner: AgentRole
      pro_score: float          # 0-100
      con_score: float          # 0-100
      reasoning: str            # paragraph-length justification
      key_winning_arguments: list[str]  # top 3 arguments that swayed the judge
      round_count: int
      total_tokens_used: int
      total_cost_usd: float
      timestamp: datetime
  ```
  - `is_tie() -> bool` always returns `False` (ties forbidden by assignment)
  - File ≤ 150 lines

### 4.2 — IPC Flow Validation

- [x] Implement routing table in `MasterAgent`: maps `AgentRole → IPCChannel`
- [x] Validate sender on every received message (reject messages from wrong sender)
- [x] Validate message type is appropriate for current debate phase
- [x] Log every IPC event: send, receive, timeout, error
- [x] Write integration tests:
  - `test_father_receives_from_pro` (mocked Pro process)
  - `test_father_forwards_to_con` (mocked Con process)
  - `test_sibling_direct_message_rejected`
  - `test_ipc_timeout_triggers_watchdog`

### 4.3 — JSON Protocol Enforcement

- [x] All IPC messages must be valid JSON (enforced by Pydantic on deserialization)
- [x] Implement `JSONProtocolValidator`:
  - `validate_message(self, raw: str) -> DebateMessage`
  - Logs malformed messages before raising
  - Never crashes process on malformed message — returns `ERROR` message type
- [x] Write unit tests:
  - `test_valid_json_passes_validation`
  - `test_malformed_json_returns_error_message`
  - `test_missing_required_field_raises`

---

## Phase 5: Debate Logic & Round Management

**Goal:** Implement the full 10+ round debate exchange.

**Completion criteria:** A complete debate runs end-to-end (mocked API) with all rounds captured in transcript.

**Dependencies:** Phase 4 complete.

### 5.1 — Debate Loop

- [x] In `DebateSession.run()`:
  ```
  STEP 1: Father opens debate — sends topic to both agents
  STEP 2: For round in range(MAX_ROUNDS):
      2a. Father requests argument from Pro (with full history)
      2b. Father forwards Pro's argument to Con
      2c. Con generates counter-argument (MUST include rebuttal of Pro's point)
      2d. Father logs round result
      2e. Father pings watchdog
      2f. If Con's argument agrees with Pro's → error + regenerate (max 2 attempts)
  STEP 3: After MIN_ROUNDS, Father checks if debate is concluded
  STEP 4: Father collects full transcript → delivers to judging module
  STEP 5: Verdict generated and returned
  ```
- [x] Enforce minimum 10 rounds before verdict
- [x] Allow configurable max rounds (default 10)
- [x] Edge case: if an agent fails to respond within timeout:
  - Log `WATCHDOG_KILL` event
  - Kill and restart process
  - Re-inject last context
  - Max 2 restart attempts; on third failure, declare that side forfeit
- [x] Write unit tests:
  - `test_debate_runs_minimum_10_rounds`
  - `test_agent_timeout_triggers_restart`
  - `test_agreement_detection_triggers_regeneration`
  - `test_debate_transcript_length_matches_rounds`

### 5.2 — Web Search Enforcement

- [x] Every argument generation MUST invoke web search tool
- [x] `BaseAgent.call_api` extracts `tool_use` blocks from response
- [x] If `tool_use` block for `web_search` is absent, raises `WebSearchNotUsedError`
- [x] `WebSearchNotUsedError` triggers one retry; if still absent on retry, logs ERROR and uses result anyway but flags in verdict
- [x] `Evidence` objects extracted from tool result and attached to `DebateMessage`
- [x] Write unit tests:
  - `test_argument_without_search_raises_error`
  - `test_retry_on_missing_search`
  - `test_evidence_extracted_from_tool_result`

### 5.3 — Agreement Detection

- [x] Implement `AgreementDetector`:
  - `is_agreeing(self, pro_message: str, con_message: str) -> bool`
  - Uses lightweight heuristic: checks for agreement phrases ("I agree", "you're right", "exactly", "correct") OR semantic similarity check via embedding (optional advanced feature)
  - Returns `True` if Con is capitulating rather than rebutting
  - File ≤ 150 lines
- [x] Write unit tests:
  - `test_detects_explicit_agreement`
  - `test_genuine_counter_argument_not_flagged`
  - `test_partial_concession_not_flagged`

---

## Phase 6: Judging System

**Goal:** Implement the Father's verdict mechanism.

**Completion criteria:** Verdict is generated with numeric scores, rationale, and correct winner identification.

**Dependencies:** Phase 5 complete.

### 6.1 — `docs/PRD_judging_algorithm.md` Implementation

- [x] `VerdictGenerator` (called from `MasterAgent.deliver_verdict`):
  - Input: full `list[RoundResult]` transcript
  - Constructs judging prompt with explicit evaluation rubric:
    - Rhetorical strength (0–25): clarity, structure, persuasive language
    - Evidence quality (0–25): relevance, credibility of web sources cited
    - Logical coherence (0–25): internal consistency, no self-contradiction
    - Counter-argument effectiveness (0–25): how well each rebuttal addressed opponent's point
  - Total score per agent: 0–100
  - Uses web search to fact-check evidence sources cited (adds credibility weight)
  - Father MUST pick a winner — never a tie
  - If scores are equal after calculation, a 5-point "rhetorical edge" tiebreaker is applied
  - Returns `Verdict` dataclass
- [x] Write unit tests:
  - `test_verdict_always_has_winner`
  - `test_scores_sum_to_100_per_dimension`
  - `test_tie_resolved_by_tiebreaker`
  - `test_reasoning_paragraph_non_empty`
  - `test_key_winning_arguments_length_three`

### 6.2 — Token & Cost Accounting

- [x] Track cumulative token usage across entire debate:
  - `DebateSession` accumulates `prompt_tokens`, `completion_tokens` per round
  - Calculates cost using model pricing from `config/setup.json`
  - Final tally included in `Verdict.total_cost_usd`
- [x] Log cost per agent per round in JSONL
- [x] Write unit tests:
  - `test_token_accumulation_across_rounds`
  - `test_cost_calculation_matches_model_pricing`

---

## Phase 7: CLI Interface

**Goal:** Build the terminal interface for running debates.

**Completion criteria:** `uv run python -m debate.sdk.sdk --topic "X vs Y"` runs a full debate and displays results.

**Dependencies:** Phase 6 complete.

### 7.1 — `src/main.py` — Entry Point

- [x] Uses `typer` for CLI (not raw `argparse`):
  ```
  Commands:
    run     Run a debate on a given topic
    replay  Replay a saved debate transcript
    status  Show gatekeeper queue status
  ```
- [x] `run` command options:
  - `--topic TEXT` (required): debate topic
  - `--rounds INT` (default: 10, min: 5): number of rounds
  - `--model TEXT` (default: from config): LLM model to use
  - `--log-level TEXT` (default: INFO)
  - `--output-dir PATH` (default: results/): where to save transcript
  - `--verbose / --no-verbose`: show live debate vs. just verdict
- [x] File ≤ 150 lines

### 7.2 — Terminal Output with `rich`

- [x] Use `rich` for formatted output:
  - Panel for each argument (color-coded: Pro=blue, Con=red, Father=yellow)
  - Progress bar for rounds
  - Final verdict displayed in a bordered box with scores as a table
  - Evidence sources listed beneath each argument (dimmed)
- [x] `--verbose` shows live streaming; `--no-verbose` shows only verdict
- [x] File ≤ 150 lines (split into `src/debate/ui/display.py` if needed)

### 7.3 — Transcript Saving

- [x] Save full transcript to `results/{session_id}_{topic_slug}.json` on completion
- [x] Transcript schema:
  ```json
  {
    "session_id": "uuid",
    "topic": "string",
    "started_at": "ISO8601",
    "completed_at": "ISO8601",
    "rounds": [...],
    "verdict": {...},
    "total_cost_usd": 0.00,
    "total_tokens": 0
  }
  ```
- [x] Write unit tests:
  - `test_transcript_saved_to_results_dir`
  - `test_transcript_is_valid_json`
  - `test_transcript_filename_contains_session_id`

---

## Phase 8: Logging, Monitoring & Observability

**Goal:** Full structured observability across all three agents.

**Completion criteria:** After a debate, `logs/` contains JSONL files with complete round-by-round records.

**Dependencies:** Phase 3 complete (LoggingMixin).

### 8.1 — JSONL Log Structure

- [x] Each agent writes to its own log file: `logs/{agent_name}_{date}.jsonl`
- [x] Father writes a master session log: `logs/session_{session_id}.jsonl`
- [x] Each log line is a valid, self-contained JSON object (JSONL format)
- [x] Log rotation: at 500 lines per file, create new file; keep max 20 files
- [x] Implement `LogRotationManager`:
  - Checks line count before each write
  - Creates new file when limit reached
  - Deletes oldest file when 20-file limit reached
  - File ≤ 150 lines

### 8.2 — Event Types to Log

- [x] `SESSION_START`: session_id, topic, config snapshot
- [x] `ROUND_START`: round number, timestamp
- [x] `API_CALL`: agent, model, prompt_tokens, completion_tokens, cost_usd, duration_ms
- [x] `TOOL_USE`: agent, tool_name, query, results_count
- [x] `IPC_SEND`: sender, recipient, message_type, round
- [x] `IPC_RECV`: receiver, sender, message_type, round
- [x] `AGREEMENT_DETECTED`: round, agent, flagged_text (triggers regeneration)
- [x] `WATCHDOG_KILL`: agent, timeout_seconds, restart_attempt
- [x] `VERDICT`: winner, scores, reasoning
- [x] `SESSION_END`: duration_seconds, total_rounds, total_cost_usd
- [x] `ERROR`: error_type, message, stack_trace, context

### 8.3 — Cost Monitoring

- [x] Real-time cost logging per API call
- [x] Running total accessible via `DebateSDK.get_cost_so_far() -> float`
- [x] Configurable budget limit in `setup.json`; warn when 80% of budget consumed
- [x] Write unit tests:
  - `test_cost_logged_per_api_call`
  - `test_budget_warning_at_80_percent`

---

## Phase 9: Testing Suite

**Goal:** Achieve ≥ 85% coverage with comprehensive tests.

**Completion criteria:** `uv run pytest tests/ --cov=src --cov-report=term-missing` shows ≥ 85% coverage; zero test failures.

**Dependencies:** All implementation phases.

### 9.1 — Test Strategy

All tests follow TDD: write tests BEFORE or ALONGSIDE implementation.

### 9.2 — `tests/conftest.py` — Shared Fixtures

- [x] `mock_anthropic_client`: returns a mock with predictable responses
- [x] `mock_gatekeeper`: passes through without rate limiting
- [x] `sample_debate_message`: factory for `DebateMessage` with web search evidence
- [x] `sample_transcript`: list of 10 `RoundResult` objects
- [x] `mock_config`: loads test-safe config values
- [x] `sample_verdict`: pre-built `Verdict` for assertion helpers
- [x] Mock for IPC channels (in-memory queues)

### 9.3 — Unit Test Coverage Requirements

For each module, tests must cover:

**`test_agents/`**
- [x] `test_base_agent.py`:
  - `test_call_api_uses_gatekeeper` — verify gatekeeper.execute is called
  - `test_web_search_mandatory` — no-evidence response raises error
  - `test_abstract_process_message_not_callable`
  - Edge case: `test_api_returns_empty_string` → raises `AgentResponseError`
- [x] `test_master_agent.py`:
  - `test_orchestrate_round_requests_from_pro_first`
  - `test_orchestrate_round_forwards_to_con`
  - `test_father_mediates_all_messages`
  - `test_verdict_always_has_winner`
  - Edge case: `test_pro_timeout_handled_gracefully`
- [x] `test_pro_subagent.py`:
  - `test_generates_evidence_based_argument`
  - `test_argument_supports_pro_position`
  - `test_skill_loaded_from_file`
- [x] `test_con_subagent.py`:
  - `test_generates_rebuttal_not_agreement`
  - `test_skill_differs_from_pro_skill`
  - `test_counter_argument_references_pro_point`

**`test_ipc/`**
- [x] `test_message.py`:
  - `test_full_serialization_round_trip`
  - `test_missing_evidence_validation_error`
  - `test_invalid_role_raises`
  - `test_message_id_is_uuid`
- [x] `test_ipc_channel.py`:
  - `test_send_receive_under_timeout`
  - `test_receive_timeout_raises`
  - `test_queue_depth_tracked`

**`test_debate/`**
- [x] `test_session.py`:
  - `test_spawns_two_child_processes`
  - `test_processes_terminated_on_completion`
  - `test_minimum_rounds_enforced`
- [x] `test_round_manager.py`:
  - `test_round_increments_correctly`
  - `test_has_minimum_rounds_false_before_10`
  - `test_transcript_correct_length`
- [x] `test_verdict.py`:
  - `test_is_tie_always_false`
  - `test_serializes_to_json`

**`test_skills/`**
- [x] `test_skill_base.py`:
  - `test_abstract_methods_enforced`
  - `test_description_non_empty`
- [x] `test_pro_skill.py` / `test_con_skill.py`:
  - `test_skill_file_exists`
  - `test_skill_description_differs_between_agents`
- [x] `test_router_skill.py`:
  - `test_routes_to_correct_skill_based_on_opening`
  - `test_irrelevant_skills_not_loaded_to_context`

**`test_shared/`**
- [x] `test_gatekeeper.py`: (see Phase 2.2)
- [x] `test_config.py`: (see Phase 2.1)
- [x] `test_watchdog.py`: (see Phase 3.2)
- [x] `test_logging_mixin.py`: (see Phase 3.1)

### 9.4 — Integration Tests

- [x] `test_full_debate.py`:
  - `test_end_to_end_debate_completes` (fully mocked API)
  - `test_verdict_generated_after_10_rounds`
  - `test_transcript_saved_correctly`
  - `test_all_messages_have_evidence`
  - `test_no_sibling_direct_messages_in_log`
- [x] `test_ipc_flow.py`:
  - `test_real_multiprocessing_queue_round_trip`
  - `test_father_correctly_routes_all_messages`
- [x] `test_gatekeeper_queue.py`:
  - `test_100_concurrent_requests_queued_correctly`
  - `test_rate_limit_not_exceeded_under_load`

### 9.5 — Edge Case & Failure Tests

- [x] Agent process crashes mid-debate → Watchdog restarts
- [x] IPC queue fills beyond max depth → backpressure error logged, not crash
- [x] API returns malformed JSON tool result → graceful error, retry
- [x] Network error during web search → agent logs warning, proceeds with prior evidence
- [x] Debate topic is empty string → `ValueError` from SDK before starting
- [x] Config file missing → `ConfigurationError` with clear message

### 9.6 — Performance Tests

- [x] Measure average round duration (target: < 30 seconds)
- [x] Measure total debate duration (target: < 10 minutes for 10 rounds)
- [x] Validate token count does not exceed session budget
- [x] Log and assert no memory leaks in long-running sessions (process memory check)

---

## Phase 10: Configuration, Security & Hardening

**Goal:** Production-grade security and zero hardcoded values.

**Completion criteria:** `ruff check` = 0 violations; `grep -r "sk-ant" src/` returns no results; all config loaded from files.

**Dependencies:** All implementation phases.

### 10.1 — Security Checklist

- [ ] `API_KEY` only via `os.environ.get("ANTHROPIC_API_KEY")` — NEVER in code
- [ ] `.env` is in `.gitignore` and never committed
- [ ] `.env.example` has all keys with placeholder values
- [ ] No hardcoded model names, timeouts, URLs, or numeric thresholds in source code
- [ ] All values come from `ConfigManager` → config JSON files → environment variables
- [ ] Run `grep -rn "sk-ant\|claude-\|api.anthropic" src/` — only constants.py references allowed
- [ ] `Gatekeeper` prevents runaway token consumption via budget cap

### 10.2 — Ruff Compliance

- [ ] Run `uv run ruff check src/ tests/` → zero violations before every commit
- [ ] Configure pre-commit hook (optional but recommended):
  ```
  uv run ruff check src/ tests/ && uv run pytest tests/ --co -q
  ```
- [ ] All imports organized (isort via ruff rule `I`)
- [ ] No unused imports (rule `F`)
- [ ] All f-strings modernized (rule `UP`)

### 10.3 — File Size Compliance

- [ ] Run: `find src/ -name "*.py" -exec wc -l {} + | sort -rn | head -20`
- [ ] Any file > 150 lines must be split
- [ ] Document split rationale in file header comment

### 10.4 — Version Management

- [ ] All JSON config files include `"version": "1.00"`
- [ ] `src/debate/shared/version.py` defines `VERSION = "1.00"`
- [ ] On startup, `ConfigManager` validates config version matches code version
- [ ] Mismatched version logs `WARNING` (not error — backwards compatible by default)

---

## Phase 11: Research, Analysis & Visualization

**Goal:** Demonstrate engineering depth through data analysis of debate outcomes.

**Completion criteria:** Notebook exists, produces visualizations, cost analysis table generated.

**Dependencies:** Phase 5+ (needs at least one complete debate transcript).

### 11.1 — `notebooks/debate_analysis.ipynb`

- [ ] Load and parse JSONL logs from `logs/`
- [ ] Compute per-round metrics:
  - Argument word count per agent per round
  - Evidence count per argument
  - API call duration per round
  - Token usage per round
- [ ] Compute aggregate metrics:
  - Win rate per agent position (Pro vs Con) across multiple debates
  - Average rounds before verdict
  - Total cost per debate
  - Cost per argument

### 11.2 — Parameter Research (Sensitivity Analysis)

- [ ] Vary `max_rounds` from 5 to 15; observe verdict stability
- [ ] Vary `temperature` (if configurable) on judge's scoring call; observe score variance
- [ ] Document findings in `results/sensitivity_analysis.md`

### 11.3 — Visualizations

Produce the following charts and save to `assets/`:

- [ ] `bar_chart_scores_by_agent.png`: per-debate Pro vs Con scores (bar chart)
- [ ] `line_chart_token_usage_by_round.png`: token accumulation per round
- [ ] `scatter_evidence_vs_score.png`: correlation between evidence count and persuasion score
- [ ] `heatmap_round_durations.png`: round × session duration heatmap
- [ ] Cost breakdown table (matching Table 4 from guidelines):
  | Model | Input Tokens | Output Tokens | Total Cost |
  |-------|-------------|---------------|------------|
  | claude-sonnet | ... | ... | $... |

### 11.4 — Prompt Engineering Log

- [ ] `prompts/prompt_log.md`:
  - Entry for each significant prompt iteration (at least 5 entries)
  - For each: objective, prompt used, sample output, improvement made
  - Final optimized prompts for Pro, Con, and Father system prompts

---

## Phase 12: Documentation & Submission

**Goal:** Complete all required documentation to maximum quality.

**Completion criteria:** README is complete, all docs exist, submission package assembled.

**Dependencies:** All phases complete.

### 12.1 — `README.md` — Comprehensive

- [ ] Project title and one-sentence description
- [ ] Architecture overview with ASCII diagram
- [ ] Installation instructions:
  ```bash
  git clone <repo>
  cd debate-agents
  cp .env.example .env
  # Edit .env with your ANTHROPIC_API_KEY
  uv sync
  ```
- [ ] Usage examples:
  ```bash
  # Run a debate
  uv run python -m debate.sdk.sdk run --topic "Is Madrid better than Barcelona?"

  # With custom rounds
  uv run python -m debate.sdk.sdk run --topic "AI is beneficial" --rounds 5

  # Verbose mode (live debate)
  uv run python -m debate.sdk.sdk run --topic "..." --verbose
  ```
- [ ] Configuration guide: all `setup.json` and `rate_limits.json` parameters explained
- [ ] Project structure (abbreviated tree)
- [ ] Testing instructions:
  ```bash
  uv run pytest tests/ --cov=src
  uv run ruff check src/ tests/
  ```
- [ ] Debate topics examples that work well
- [ ] Budget note: if reducing to 5 pings, explicitly document in README per assignment guidelines
- [ ] Sample output (with redacted API key)
- [ ] License + attribution to course
- [ ] Links to `docs/` documents

### 12.2 — Session Screenshots

- [ ] Capture at least 3 terminal screenshots:
  - `assets/screenshot_debate_running.png`: live debate in progress
  - `assets/screenshot_verdict.png`: final verdict display
  - `assets/screenshot_test_coverage.png`: pytest coverage report showing ≥ 85%
- [ ] Include in README.md

### 12.3 — Final Pre-Submission Checklist

Run through Phase 15 (Quality Gates) completely before submission.

- [ ] `uv run ruff check src/ tests/` → 0 violations
- [ ] `uv run pytest tests/ --cov=src --cov-fail-under=85` → PASS
- [ ] `grep -rn "sk-ant" src/` → 0 results
- [ ] All files ≤ 150 lines (run `wc -l` check)
- [ ] `.env` NOT committed (check `git status`)
- [ ] `uv.lock` IS committed
- [ ] `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` all exist
- [ ] All four per-algorithm PRDs exist
- [ ] `README.md` includes session log path and screenshots
- [ ] Debate runs successfully end-to-end
- [ ] Verdict always produced (never crashes)
- [ ] GitHub repo is public (or shared with instructor per instructions)
- [ ] PDF link submitted on Moodle
- [ ] Both partners submitted separately on Moodle

---

## Quality Gates & Phase Completion Checklist

Before advancing to the next phase, all items in the current phase must pass:

| Gate | Criterion | Tool |
|------|-----------|------|
| G0 | All planning docs exist and reviewed | Manual |
| G1 | `uv sync` succeeds, `ruff check` = 0 | `uv`, `ruff` |
| G2 | Gatekeeper unit tests pass | `pytest` |
| G3 | Agent base classes pass unit tests | `pytest` |
| G4 | IPC round-trip integration test passes | `pytest` |
| G5 | Full debate loop runs (mocked) | `pytest` |
| G6 | Verdict generated with scores | `pytest` |
| G7 | CLI accepts topic and outputs verdict | Manual |
| G8 | Logs written in JSONL format | Manual + `pytest` |
| G9 | Coverage ≥ 85% | `pytest --cov` |
| G10 | No hardcoded values | `grep` audit |
| G11 | All files ≤ 150 lines | `wc -l` |
| G12 | Notebook produces charts | Manual |
| G13 | README complete with screenshots | Manual |

---

## Creative Extensions (Phases 9-18)

- [x] Hitchens vs Chomsky famous debater personas
- [x] RAG retriever with real knowledge bases (data/hitchens.md, data/chomsky.md)
- [x] Dynamic Pro/Con role assignment based on topic
- [x] RBG judge persona
- [x] Multiprocessing dotenv fix
- [x] Parallel tool call handling
- [x] Cost optimizations (haiku model, clamped tokens, limited history)

### Upcoming Tasks
- [ ] Score timeline visualization (phase 10)
- [ ] Cinematic README (phase 11)
- [ ] Final cleanup and ruff (phase 12)

## Nice-to-Have Improvements

These items improve the submission quality but are not strictly required by the assignment. Implement after all core requirements pass.

### N1 — Replay System
- [ ] `uv run python -m debate.sdk.sdk replay --file results/{session_id}.json`
- [ ] Re-renders saved debate transcript with same rich formatting
- [ ] Useful for demonstration without consuming API tokens

### N2 — Multi-Topic Comparison
- [ ] Accept multiple `--topic` flags; run debates in sequence
- [ ] Produce comparison report: which topic type led to more balanced debates?

### N3 — Budget Protection CLI Flag
- [ ] `--max-cost-usd 1.00`: abort debate if cost exceeds limit
- [ ] Displays running cost in progress bar

### N4 — Debate Export
- [ ] `--export-html`: saves debate as formatted HTML for browser viewing
- [ ] `--export-md`: saves debate as Markdown document

### N5 — Interactive Mode
- [ ] After verdict, prompt user: "Ask the judge a follow-up question?"
- [ ] Judge answers using full transcript as context (one additional API call)

### N6 — Configurable Debate Styles
- [ ] Oxford-style (formal): strict turn-taking, no interruptions
- [ ] Socratic: judge asks clarifying questions mid-debate
- [ ] Crossfire: agents can request evidence challenges

---

## Creative / Advanced Features

> These features go significantly beyond the homework requirements. Implement any of these to stand out as an elite submission. Each is self-contained and can be added without breaking the core system.

---

### A1 — Live Debate Dashboard (Terminal UI)

**Description:** Replace plain `rich` output with a full-screen TUI dashboard using `textual` library.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  🎙 AI DEBATE SYSTEM   Topic: Madrid vs Barcelona    Round 7 / 10   │
├───────────────────────────┬─────────────────────────────────────────┤
│  PRO AGENT               │  CON AGENT                               │
│  Score: 68.3             │  Score: 71.4                             │
│  Evidence Used: 12       │  Evidence Used: 15                       │
│  ─────────────────────── │  ─────────────────────────────────────── │
│  [Argument text here...] │  [Counter-argument here...]              │
│                          │                                          │
├───────────────────────────┴─────────────────────────────────────────┤
│  JUDGE:  Round 7 received. Forwarding to Con agent...               │
│  💰 Cost: $0.042 / $1.00 budget  │  📊 Tokens: 4,231               │
└─────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
- [ ] `src/debate/ui/dashboard.py` using `textual`
- [ ] Live updates via `textual` workers (non-blocking)
- [ ] Color-coded: Pro=blue, Con=red, Father=gold
- [ ] Real-time cost and token meter
- [ ] Evidence panel showing sources used per argument
- [ ] Dismissable with `q`; falls back to plain output if `textual` not installed

---

### A2 — Adaptive Judging System

**Description:** The Judge agent adapts its evaluation rubric based on the debate topic category.

**Features:**
- [ ] Topic classifier (pre-debate): detects if topic is **scientific**, **political**, **philosophical**, or **cultural** using a lightweight API call
- [ ] Different rubric weights per category:
  - Scientific: evidence quality 40%, logical coherence 35%, rhetoric 25%
  - Political: rhetoric 40%, evidence 30%, coherence 30%
  - Philosophical: logical coherence 45%, rhetoric 30%, evidence 25%
- [ ] Rubric choice logged and disclosed in verdict reasoning
- [ ] `docs/PRD_adaptive_judging.md` documents the algorithm

---

### A3 — Memory System with Episodic Recall

**Description:** Each Subagent builds an episodic memory of its strongest and weakest arguments across rounds, enabling strategic evolution.

**Features:**
- [ ] `EpisodicMemory` class per agent:
  - Stores each argument with its "effectiveness score" (inferred from judge's intermediate feedback)
  - `get_strongest_arguments(n=3) -> list[str]`
  - `get_patterns_to_avoid() -> list[str]` (arguments the judge rated poorly)
- [ ] After each round, Father provides one-line coaching note to each agent (private, not shared with opponent): "Your use of statistics was compelling" or "Your point lacked specificity"
- [ ] Agents incorporate coaching into next argument
- [ ] Memory serialized to `results/{session_id}_memory.json`
- [ ] Measurable improvement metric: compare argument quality score round 1 vs round 10

---

### A4 — Experiment Tracking & Replay System

**Description:** Full MLOps-style experiment tracking for debates.

**Features:**
- [ ] `ExperimentTracker` class:
  - Assigns each debate an `experiment_id`
  - Tracks: topic, config, per-round scores (inferred), final verdict, total cost
  - Saves to `results/experiments.jsonl` (append mode)
- [ ] `uv run python -m debate.sdk.sdk experiments list`: table of all past experiments
- [ ] `uv run python -m debate.sdk.sdk experiments compare --ids exp1,exp2`: compare two debate runs
- [ ] `uv run python -m debate.sdk.sdk experiments replay --id exp1`: replay with same config
- [ ] Configurable: tag experiments with `--tag "baseline"`, `--tag "with-memory"`

---

### A5 — Self-Improving Agents via Reflection

**Description:** After the debate concludes, each agent is given the opportunity to "reflect" — receiving the full transcript and the verdict, then generating a self-critique and improvement plan.

**Features:**
- [ ] Post-debate reflection call per agent (one additional API call each)
- [ ] Reflection prompt: "You just debated. The judge said: {verdict_reasoning}. Your score was {score}/100. In 3 bullet points, what would you do differently?"
- [ ] Reflections saved to `results/{session_id}_reflections.json`
- [ ] Reflections optionally injected as system prompt context in next debate (evolution feature)
- [ ] Metric: track average score improvement across successive debates on same topic

---

### A6 — Semantic Similarity Agreement Detector

**Description:** Replace the heuristic agreement detector with a proper semantic similarity check.

**Features:**
- [ ] Use the Anthropic API (small, fast call) to classify if Con's argument is a genuine rebuttal or a capitulation
- [ ] Prompt: "On a scale of 0-100, how much does Response B rebut Response A? 0 = complete agreement, 100 = complete opposition."
- [ ] Threshold configurable in `setup.json` (default: < 30 = flagged as agreement)
- [ ] Fallback to heuristic if semantic check call fails
- [ ] Log agreement scores per round in JSONL for analysis

---

### A7 — Multi-Debate Tournament System

**Description:** Simulate a debate tournament across multiple related topics.

**Features:**
- [ ] `tournament` CLI command:
  ```bash
  uv run python -m debate.sdk.sdk tournament --topics topics.json
  ```
- [ ] `topics.json` format: list of debate propositions
- [ ] Runs debates sequentially (rate-limit safe)
- [ ] Tracks win/loss per position (Pro vs Con) across all topics
- [ ] Produces tournament bracket visualization in HTML
- [ ] Identifies: "Which position (Pro or Con) wins more often?"
- [ ] Statistical significance test on win rates (chi-squared)

---

### A8 — RouterSkill Intelligence Optimization

**Description:** Implement the full RouterSkill as described in the lecture — the most memory-efficient approach to skill management.

**Features:**
- [ ] `RouterSkill` always loaded in system prompt (small, fast)
- [ ] RouterSkill reads only the opening message/question
- [ ] From it, selects top 2 relevant Skills by description match
- [ ] Only those 2 Skills are loaded into context — all others stay on disk
- [ ] Measured reduction: baseline (all skills loaded) vs. optimized (RouterSkill filtered)
- [ ] Document token savings per debate in `results/skill_routing_analysis.md`

---

### A9 — Debate Scoring Visualization with Time-Series

**Description:** Post-debate interactive visualization of how persuasion scores evolved round by round.

**Features:**
- [ ] After each round, Father estimates current score (lightweight call)
- [ ] `results/{session_id}_score_timeline.json` stores per-round scores
- [ ] `uv run python -m debate.sdk.sdk visualize --id {session_id}`: generates:
  - Line chart: Pro score vs Con score over rounds (matplotlib/plotly)
  - Bar chart: evidence count per round per agent
  - Scatter: argument length vs score increment
- [ ] Saved to `assets/{session_id}/`
- [ ] Optionally shown in terminal as ASCII art (using `plotext` library)

---

### A10 — Stress-Test & Benchmark Suite

**Description:** Dedicated benchmark suite that measures system reliability under stress.

**Features:**
- [ ] `tests/benchmarks/test_stress.py`:
  - `test_100_sequential_gatekeeper_calls`: verify no rate limit violations
  - `test_ipc_channel_1000_messages`: throughput test
  - `test_concurrent_debate_sessions`: two sessions simultaneously (uses extra tokens — mock API)
  - `test_watchdog_recovery_time`: measure restart latency
- [ ] Benchmark results saved to `results/benchmark_report.md`
- [ ] Compare: with Gatekeeper vs. without (monkey-patched) — show rate limit enforcement value
- [ ] Run benchmarks separately from unit tests: `uv run pytest tests/benchmarks/ -v`

---

*This TODO.md serves as the single source of truth for all implementation decisions. Every task here maps to at least one requirement in `docs/PRD.md` or the assignment specification. No implementation detail is left to interpretation.*

*Last updated: 2026 | Version: 1.00 | Status: Engineering Execution Plan*
