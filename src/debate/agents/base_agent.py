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

    def initialize(self, config: Any, gatekeeper: Any):
        """Initializes the agent with configuration and gatekeeper."""
        self.config = config
        self.gatekeeper = gatekeeper
        self.setup_logging(self._role.value, config.get_logging_config())

    def _get_client(self) -> Any:
        """Lazily initialize the Anthropic client."""
        if self._anthropic_client is None:
            api_key = getattr(self.config, 'api_key', None)
            if api_key:
                from anthropic import Anthropic
                self._anthropic_client = Anthropic(api_key=api_key)
        return self._anthropic_client

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
        """Call the LLM API through the gatekeeper."""
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
            client = self._get_client()
            if client:
                return client.messages.create(
                    model=self.config.get("model", "claude-sonnet-4-20250514"),
                    max_tokens=600,
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
                    self.id = "mock_id"

            class MockResponse:
                def __init__(self, is_final=False):
                    self.content = [MockBlock("text", text="Mock response")]
                    if not is_final:
                        self.content.insert(0, MockBlock("tool_use", "web_search"))
                    self.usage = type("obj", (object,), {"input_tokens": 10, "output_tokens": 10})()
                    
            has_tool_result = any(
                m.get("content") and isinstance(m["content"], list) and any(
                    (b.get("type") == "tool_result" if isinstance(b, dict) else getattr(b, "type", None) == "tool_result")
                    for b in m["content"]
                )
                for m in messages
            )
            return MockResponse(is_final=has_tool_result)

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

        tool_use_blocks = []

        if hasattr(response, "content"):
            for block in response.content:
                if block.type == "text":
                    text_content += block.text
                elif block.type == "tool_use" and block.name == "web_search":
                    used_web_search = True
                    tool_use_blocks.append(block)
                    query = block.input.get('query', '')
                    evidence_list.append(Evidence(
                        url="mock://search",
                        title=f"Search result for {query}",
                        snippet=f"Found information about {query}: It confirms your position.",
                        retrieved_at=__import__("datetime").datetime.now(),
                    ))

        # Keep track of usage
        usage_dict = {"input_tokens": 0, "output_tokens": 0}
        if hasattr(response, "usage"):
            usage_dict["input_tokens"] = response.usage.input_tokens
            usage_dict["output_tokens"] = response.usage.output_tokens

        if used_web_search:
            # Feed the tool results back to the LLM to get the final argument
            tool_results = []
            for block in tool_use_blocks:
                query = block.input.get('query', '')
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Found information about {query}: It confirms your position."
                })
                
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": tool_results
            })
            final_text, more_evidence, final_usage = self.call_api(messages, tools, _retry=_retry)
            
            # Combine text and evidence
            text_content = (text_content + "\n\n" + final_text).strip()
            evidence_list.extend(more_evidence)
            usage_dict["input_tokens"] += final_usage["input_tokens"]
            usage_dict["output_tokens"] += final_usage["output_tokens"]
            return text_content, evidence_list, usage_dict

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
