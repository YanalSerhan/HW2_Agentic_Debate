from abc import ABC, abstractmethod
from typing import Any

from debate.constants import AgentRole
from debate.ipc.ipc_mixin import IPCMixin
from debate.ipc.message import DebateMessage, Evidence
from debate.shared.logging_mixin import LoggingMixin
from debate.shared.watchdog import WatchdogMixin


class WebSearchNotUsedError(Exception):
    """Raised when the API response does not include a web search tool use."""
    pass

class BaseAgent(ABC, LoggingMixin, WatchdogMixin, IPCMixin):
    """Abstract base agent."""

    def __init__(self, role: AgentRole, session_id: str):
        LoggingMixin.__init__(self)
        WatchdogMixin.__init__(self)
        IPCMixin.__init__(self)
        self._role = role
        self._session_id = session_id
        self.config = None
        self.gatekeeper = None
        self._anthropic_client = None

    def initialize(self, config: Any, gatekeeper: Any, client: Any = None):
        """Initializes the agent with configuration and gatekeeper."""
        self.config = config
        self.gatekeeper = gatekeeper
        self._anthropic_client = client if client is not None else getattr(config, 'client', None)
        self.setup_logging(self._role.value, config.get_logging_config())

    @abstractmethod
    def process_message(self, message: DebateMessage) -> DebateMessage:
        """Processes an incoming message and returns a response."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Returns the system prompt for this agent."""
        pass

    def get_role(self) -> AgentRole:
        """Returns the role of this agent."""
        return self._role

    def get_session_id(self) -> str:
        """Returns the session ID."""
        return self._session_id

    def call_api(
        self, messages: list, tools: list, *, _retry: bool = False,
    ) -> tuple[str, list[Evidence], dict]:
        """Call the LLM API through the gatekeeper.

        Ensures web_search is used. On the first failure a single retry is
        attempted; on the second failure the result is returned anyway but
        the missing-search flag is set so the verdict can note it.
        """
        # Ensure web_search is in the tools list
        has_web_search = (
            any(t.get("name") == "web_search" for t in tools) if tools else False
        )
        if not has_web_search:
            tools = tools or []
            tools.append({
                "name": "web_search",
                "description": "Search the web for evidence.",
                "input_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            })

        def do_api_call():
            if self._anthropic_client:
                return self._anthropic_client.messages.create(
                    model=self.config.get("model", "claude-sonnet-4-20250514"),
                    max_tokens=1000,
                    system=self.get_system_prompt(),
                    messages=messages,
                    tools=tools,
                )
            # Default mock behaviour when no client is provided
            class MockBlock:
                def __init__(self, t, n="", text="Mock response"):
                    self.type = t
                    self.name = n
                    self.text = text
                    self.input = {"query": "mock query"}

            class MockResponse:
                content = [
                    MockBlock("tool_use", "web_search"),
                    MockBlock("text", text="Mock response"),
                ]
                usage = type(
                    "obj", (object,), {"input_tokens": 10, "output_tokens": 10}
                )()

            return MockResponse()

        response = self.gatekeeper.execute(do_api_call)

        # Log cost
        if hasattr(response, "usage"):
            self.log_api_call(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                cost_usd=0.0,
            )

        # Extract text and tool_use blocks
        text_content = ""
        used_web_search = False
        evidence_list: list[Evidence] = []

        if hasattr(response, "content"):
            for block in response.content:
                if block.type == "text":
                    text_content += block.text
                elif block.type == "tool_use" and block.name == "web_search":
                    used_web_search = True
                    evidence_list.append(Evidence(
                        url="mock://search",
                        title=f"Search result for {block.input.get('query', '')}",
                        snippet="Mock snippet",
                        retrieved_at=__import__("datetime").datetime.now(),
                    ))

        # Keep track of usage
        usage_dict = {"input_tokens": 0, "output_tokens": 0}
        if hasattr(response, "usage"):
            usage_dict["input_tokens"] = response.usage.input_tokens
            usage_dict["output_tokens"] = response.usage.output_tokens

        if not used_web_search:
            if not _retry:
                # One automatic retry
                self.log_event(
                    "RETRY",
                    {"reason": "web_search tool not used, retrying"},
                )
                return self.call_api(messages, tools, _retry=True)
            # Second failure — log and return result anyway (flagged)
            self.log_event(
                "ERROR",
                {"reason": "web_search tool missing after retry, proceeding"},
            )
            self._web_search_missing = True

        return text_content, evidence_list, usage_dict
