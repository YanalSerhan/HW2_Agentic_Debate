
from debate.constants import AgentRole
from debate.ipc.ipc_channel import IPCChannel
from debate.ipc.message import DebateMessage


class IPCError(Exception):
    """Raised on invalid IPC routing."""
    pass

class IPCMixin:
    """Mixin to handle IPC messaging and logging."""

    def __init__(self):
        self._ipc_channels: dict[AgentRole, IPCChannel] = {}

    def set_ipc_channel(self, role: AgentRole, channel: IPCChannel):
        """Sets an IPC channel for communication with the given role."""
        self._ipc_channels[role] = channel

    def send_to_father(self, message: DebateMessage):
        """Sends a message to the father agent."""
        if self.get_role() == AgentRole.FATHER:
            raise IPCError("Father cannot send to itself via child method")

        if message.recipient != AgentRole.FATHER:
            raise IPCError(f"Invalid routing: Child attempted to send direct to {message.recipient}")

        if AgentRole.FATHER not in self._ipc_channels:
            raise IPCError("No IPC channel established with Father")

        self._ipc_channels[AgentRole.FATHER].send(message)

        if hasattr(self, "log_event"):
            self.log_event("IPC_SEND", {"to": "father", "message_id": message.message_id, "type": message.message_type.value})

    def send_to_child(self, agent_role: AgentRole, message: DebateMessage):
        """Sends a message to a specific child agent. For Father only."""
        if self.get_role() != AgentRole.FATHER:
            raise IPCError("Only Father can use send_to_child")

        if message.recipient != agent_role:
            raise IPCError(f"Message recipient {message.recipient} does not match channel {agent_role}")

        if agent_role not in self._ipc_channels:
            raise IPCError(f"No IPC channel established with {agent_role}")

        self._ipc_channels[agent_role].send(message)

        if hasattr(self, "log_event"):
            self.log_event("IPC_SEND", {"to": agent_role.value, "message_id": message.message_id, "type": message.message_type.value})

    def receive_message(self, channel_role: AgentRole, timeout: float = 30.0) -> DebateMessage:
        """Receives a message from the specified channel."""
        if channel_role not in self._ipc_channels:
            raise IPCError(f"No IPC channel established with {channel_role}")

        message = self._ipc_channels[channel_role].receive(timeout=timeout)

        if hasattr(self, "log_event"):
            self.log_event("IPC_RECV", {"from": channel_role.value, "message_id": message.message_id, "type": message.message_type.value})

        return message

    def get_role(self) -> AgentRole:
        """Should be implemented by the subclass."""
        raise NotImplementedError
