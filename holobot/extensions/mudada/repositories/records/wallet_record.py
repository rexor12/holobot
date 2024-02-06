from dataclasses import dataclass

from holobot.sdk.database.repositories import Record, manually_generated_key

@manually_generated_key
@dataclass
class WalletRecord(Record[str]):
    id: str
    amount: int
