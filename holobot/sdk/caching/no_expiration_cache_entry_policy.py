from .cache_entry_policy import CacheEntryPolicy

class NoExpirationCacheEntryPolicy(CacheEntryPolicy):
    def is_expired(self) -> bool:
        return False
