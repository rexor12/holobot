from dataclasses import dataclass
from datetime import timedelta

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class InteractableAuthorizationRecord(Record):
    interactable_id: PrimaryKey[str]
    server_id: PrimaryKey[str]
    status: bool
