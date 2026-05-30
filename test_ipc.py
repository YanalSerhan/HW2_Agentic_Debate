from debate.constants import MessageType
from debate.ipc.message import DebateMessage
from datetime import datetime, timezone

m = DebateMessage(message_id="1", session_id="1", sender=1, recipient=1, message_type=MessageType.ARGUMENT, round_number=1, content="test", evidence=[], timestamp=datetime.now(timezone.utc))
print(m.message_type.ARGUMENT)
