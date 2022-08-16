from dataclasses import dataclass

@dataclass
class Message:
    server_id: str | None
    channel_id: str
    message_id: str
