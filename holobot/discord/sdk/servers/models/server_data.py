from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class ServerData:
    server_id: int
    icon_url: str | None
    banner_url: str | None
    name: str
    owner_id: int
