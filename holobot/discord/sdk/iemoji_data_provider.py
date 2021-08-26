from .models import Emoji, InteractionContext
from typing import Optional

class IEmojiDataProvider:
    async def find_emoji(self, context: InteractionContext, name_or_mention: str) -> Optional[Emoji]:
        raise NotImplementedError
