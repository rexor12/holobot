from typing import Protocol

from holobot.extensions.mudada.models import UserReward
from holobot.sdk.database.repositories import IRepository

class IUserRewardRepository(
    IRepository[int, UserReward],
    Protocol
):
    ...
