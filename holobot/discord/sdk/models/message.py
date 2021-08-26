from dataclasses import dataclass

@dataclass
class Message:
    channel_id: str
    message_id: str
