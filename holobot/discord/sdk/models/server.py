from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Server:
    identifier: str
    owner_id: Optional[str]
    owner_name: Optional[str]
    name: str
    member_count: Optional[int]
    icon_url: Optional[str]
    is_large: Optional[bool]
    joined_at: Optional[datetime]
    shard_id: Optional[int]
    