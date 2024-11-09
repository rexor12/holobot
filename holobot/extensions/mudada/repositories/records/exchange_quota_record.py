from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class ExchangeQuotaRecord(Record):
    id: PrimaryKey[int]
    amount: int
    exchanged_amount: int
    lost_amount: int
