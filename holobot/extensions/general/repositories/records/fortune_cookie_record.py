from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass
class FortuneCookieRecord(Record):
    id: PrimaryKey[int]
    message: str
