from typing import Protocol

from holobot.extensions.mudada.models import HalloweenReward
from holobot.sdk.database.repositories import IRepository

class IHalloweenRewardRepository(IRepository[str, HalloweenReward], Protocol):
    ...
