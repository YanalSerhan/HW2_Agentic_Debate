# Product Requirements Document (PRD)
## Multi-Agent AI Debate System

### 1. Project Overview
**Purpose**: To build a three-agent debate system implemented in Python, where a Father/Judge agent orchestrates a debate between a Pro agent and a Con agent. The system evaluates arguments based on persuasive power rather than factual correctness.
**Context**: This is Exercise 02 for the "Agents, Subagents, Commands and Skills" course (Lesson 05).
**Academic Constraints**: Strict adherence to assignment constraints including Python IPC, JSON serialization, a minimum of 10 debate rounds, mandatory web search usage, TDD with 85%+ coverage, Ruff compliance, structured logging, and OOP architecture with no direct sibling communication.

### 2. Stakeholder Goals
- **Student Submission**: Deliver a high-quality, fully compliant project demonstrating mastery of multi-agent architectures, IPC, and rigorous software engineering practices.
- **AI Grader Evaluation**: Provide structured, readable logs, clear documentation, comprehensive tests, and an architecture that strictly follows the stated requirements to ensure maximum grading score.

### 3. User Stories
- As a user, I can specify a debate topic via CLI and receive a final verdict with a persuasion score.
- As a user, I can observe the full debate transcript in real time.
- As a user, I can adjust the number of debate rounds (down to 5 if budget-limited) via configuration.
- As a user, I can review structured logs (JSONL format) of all agent interactions for debugging and analysis.

### 4. Functional Requirements
- **Three-Process Architecture**: Implement Father, Pro, and Con agents as separate OS processes.
- **Debate Rounds**: Ensure a minimum of 10 exchange rounds per agent side (10 arguments + 10 counter-arguments).
- **Web Search**: Integrate a mandatory web search tool (`tool_use`) that must be used in every agent's reasoning.
- **JSON Serialization**: Use JSON for all inter-process communication (IPC) messages.
- **Routing**: Ensure Father mediates all communication (no direct child-to-child communication).
- **Unique Skills**: Assign unique skills to the Pro and Con agents.
- **Verdict Delivery**: Deliver a final verdict with an explicit scoring rationale based on persuasive power, not factual truth.

### 5. Non-Functional Requirements
- **Performance**: Response timeout ≤ 30 seconds per agent turn.
- **Reliability**: Graceful degradation if one agent times out (Watchdog pattern for recovery).
- **Observability**: Structured JSONL logging, rotating at 20 files × 500 lines.
- **Security**: Zero hardcoded secrets or configuration values.
- **Code Quality**: 85%+ test coverage (TDD approach), zero Ruff linting violations, no file > 150 lines of code.

### 6. Out-of-Scope Items
- GUI (terminal-only interface per assignment).
- Persistent debate history across sessions (database integration).
- Multi-topic simultaneous debates (extension only).

### 7. Acceptance Criteria & KPIs
- **Completion**: Debate completes successfully with ≥ 10 rounds.
- **Verdict**: A verdict is delivered with a numeric persuasion score per agent and no ties.
- **Validation**: All IPC messages validate against a defined JSON schema.
- **Testing**: All unit and integration tests pass, with coverage ≥ 85%.

### 8. Assumptions & Dependencies
- An Anthropic API key is available in the environment.
- `uv` is installed and serves as the sole package manager.
- System is running Python 3.10+.
