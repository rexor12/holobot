from .channel import Channel
from dataclasses import dataclass, field
from typing import List

@dataclass
class AudioChannel(Channel):
    member_ids: List[str] = field(default_factory=lambda: [])
