from dataclasses import dataclass

@dataclass
class ServerData:
    server_id: str
    icon_url: str | None
    name: str
