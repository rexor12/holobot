from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.user_profiles import UserProfile
from holobot.sdk.database.repositories import IRepository

class IUserProfileRepository(IRepository[str, UserProfile], Protocol):
    ...
