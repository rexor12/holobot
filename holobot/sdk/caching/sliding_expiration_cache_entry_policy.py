from datetime import datetime, timedelta

from holobot.sdk.utils.datetime_utils import utcnow
from .cache_entry_policy import CacheEntryPolicy

class SlidingExpirationCacheEntryPolicy(CacheEntryPolicy):
    """A cache entry policy with a sliding window expiration."""

    @property
    def expires_after(self) -> timedelta:
        """Gets the duration of time since the last access
        after which the item expires.

        :return: The duration of time since the last access after which the item expires.
        :rtype: timedelta
        """

        return self.__expires_after

    @property
    def expires_at(self) -> datetime:
        """Gets the date and time at which the item expires/expired.

        :return: The date and time at which the item expires/expired.
        :rtype: datetime
        """

        return self.__expires_at

    def __init__(
        self,
        expires_after: timedelta
    ) -> None:
        super().__init__()
        self.__expires_after = expires_after
        self.__expires_at = utcnow() + expires_after

    def is_expired(self) -> bool:
        return utcnow() >= self.__expires_at

    def on_entry_accessed(self) -> None:
        self.__expires_at = utcnow() + self.__expires_after
