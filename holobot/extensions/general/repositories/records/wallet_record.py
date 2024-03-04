from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class WalletRecord(Record):
    user_id: PrimaryKey[str]
    currency_id: PrimaryKey[int]
    server_id: PrimaryKey[str]
    amount: int
