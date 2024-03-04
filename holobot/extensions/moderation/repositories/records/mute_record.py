from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class MuteRecord(Record):
    id: PrimaryKey[int]
    server_id: str
    user_id: str
