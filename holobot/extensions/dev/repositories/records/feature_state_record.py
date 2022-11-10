from dataclasses import dataclass

from holobot.sdk.database.repositories import Entity, manually_generated_key

@manually_generated_key
@dataclass
class FeatureStateRecord(Entity[str]):
    id: str
    is_enabled: bool
