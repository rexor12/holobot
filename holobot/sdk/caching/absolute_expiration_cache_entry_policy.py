from datetime import datetime

from holobot.sdk.utils.datetime_utils import utcnow
from .cache_entry_policy import CacheEntryPolicy

class AbsoluteExpirationCacheEntryPolicy(CacheEntryPolicy):
    """A cache entry policy with an absolute expiration."""

    @property
    def expires_at(self) -> datetime:
        """Gets the date and time at which the item expires/expired.

        :return: The date and time at which the item expires/expired.
        :rtype: datetime
        """

        return self.__expires_at

    def __init__(
        self,
        expires_at: datetime
    ) -> None:
        super().__init__()
        self.__expires_at = expires_at

    def is_expired(self) -> bool:
        return utcnow() >= self.__expires_at
