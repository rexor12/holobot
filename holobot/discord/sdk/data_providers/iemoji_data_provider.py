from abc import ABCMeta, abstractmethod

from ..models import Emoji

class IEmojiDataProvider(metaclass=ABCMeta):
    @abstractmethod
    async def find_emoji(self, name_or_mention: str) -> Emoji | None:
        ...
