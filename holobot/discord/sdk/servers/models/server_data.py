from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerData:
    server_id: str
    icon_url: Optional[str]
    name: str
