from typing import Protocol

from holobot.extensions.mudada.models import EasterReward
from holobot.sdk.database.repositories import IRepository

class IEasterRewardRepository(IRepository[int, EasterReward], Protocol):
    ...
