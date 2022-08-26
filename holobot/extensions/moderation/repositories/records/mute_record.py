from dataclasses import dataclass

from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class MuteRecord(Entity[int]):
    id: int
    server_id: str
    user_id: str
