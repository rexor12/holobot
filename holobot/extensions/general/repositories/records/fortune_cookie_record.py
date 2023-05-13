from dataclasses import dataclass

from holobot.sdk.database.repositories import Record

@dataclass
class FortuneCookieRecord(Record[int]):
    id: int
    message: str
