from abc import ABCMeta, abstractmethod

class CacheEntryPolicy(metaclass=ABCMeta):
    """Abstract base class for cache entry policies."""

    @abstractmethod
    def is_expired(self) -> bool:
        """Determines whether the associated item has expired.

        :return: True, if the associated item has expired.
        :rtype: bool
        """
        ...

    def on_entry_accessed(self) -> None:
        """A callback invoked when the associated item has been accessed.

        This method does nothing unless an inheritor overrides it.
        """
        pass
