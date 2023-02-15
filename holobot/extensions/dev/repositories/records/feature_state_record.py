from dataclasses import dataclass

from holobot.sdk.database.repositories import Record, manually_generated_key

@manually_generated_key
@dataclass
class FeatureStateRecord(Record[str]):
    id: str
    is_enabled: bool
