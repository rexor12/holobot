from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    server_id: Optional[str]
    channel_id: str
    message_id: str
