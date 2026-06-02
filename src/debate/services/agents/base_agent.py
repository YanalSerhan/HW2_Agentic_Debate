"""Auto-generated docstring."""

from abc import ABC, abstractmethod
from typing import Any

from debate.services.agents.api_mixin import ApiMixin
from debate.services.ipc.ipc_mixin import IPCMixin
from debate.services.ipc.message import DebateMessage
from debate.shared.constants import AgentRole
from debate.shared.logging_mixin import LoggingMixin
from debate.shared.watchdog import WatchdogMixin


class WebSearchNotUsedError(Exception):
    """Raised when the API response does not include a web search tool use."""

    pass

class BaseAgent(ABC, LoggingMixin, WatchdogMixin, IPCMixin, ApiMixin):
    """Abstract base agent."""

    def __init__(self, role: AgentRole, session_id: str):
        """Auto-generated docstring."""
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
