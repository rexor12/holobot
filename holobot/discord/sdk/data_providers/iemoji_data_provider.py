from ..models import Emoji
from abc import ABCMeta, abstractmethod
from typing import Optional

class IEmojiDataProvider(metaclass=ABCMeta):
    @abstractmethod
    async def find_emoji(self, name_or_mention: str) -> Optional[Emoji]:
        ...
