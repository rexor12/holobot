from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot
from .interactable_authorization_id import InteractableAuthorizationId

@dataclass(kw_only=True)
class InteractableAuthorization(AggregateRoot[InteractableAuthorizationId]):
    status: bool
