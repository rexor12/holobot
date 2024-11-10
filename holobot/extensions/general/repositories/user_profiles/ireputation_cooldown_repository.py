from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.user_profiles import ReputationCooldown
from holobot.sdk.database.repositories import IRepository

class IReputationCooldownRepository(IRepository[int, ReputationCooldown], Protocol):
    ...
