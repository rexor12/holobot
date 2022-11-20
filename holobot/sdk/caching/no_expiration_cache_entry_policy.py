from .cache_entry_policy import CacheEntryPolicy

class NoExpirationCacheEntryPolicy(CacheEntryPolicy):
    """A cache entry policy with no expiration."""

    def is_expired(self) -> bool:
        return False
