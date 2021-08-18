from .models import Reaction
from typing import Callable, Optional

class IMessaging:
    async def send_dm(self, user_id: str, message: str) -> None:
        raise NotImplementedError

    async def send_guild_message(self, channel_id: str, message: str) -> None:
        raise NotImplementedError
    
    async def wait_for_reaction(self, filter: Optional[Callable[[Reaction], bool]] = None, timeout: int = 60) -> Reaction:
        raise NotImplementedError
