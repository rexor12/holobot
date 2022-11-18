from abc import ABCMeta, abstractmethod

class CacheEntryPolicy(metaclass=ABCMeta):
    @abstractmethod
    def is_expired(self) -> bool:
        ...

    def on_entry_accessed(self) -> None:
        pass
