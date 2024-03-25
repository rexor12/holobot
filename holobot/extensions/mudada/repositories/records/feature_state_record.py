from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class FeatureStateRecord(Record):
    id: PrimaryKey[str]
    is_enabled: bool
