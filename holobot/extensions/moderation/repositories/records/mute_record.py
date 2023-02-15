from dataclasses import dataclass

from holobot.sdk.database.repositories import Record

@dataclass(kw_only=True)
class MuteRecord(Record[int]):
    id: int
    server_id: str
    user_id: str
