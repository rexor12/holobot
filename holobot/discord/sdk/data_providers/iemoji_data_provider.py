from ..models import Emoji
from abc import ABCMeta, abstractmethod

class IEmojiDataProvider(metaclass=ABCMeta):
    @abstractmethod
    async def find_emoji(self, name_or_mention: str) -> Emoji | None:
        ...
