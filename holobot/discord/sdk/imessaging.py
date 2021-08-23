from .models import Reaction
from typing import Callable, Optional

class IMessaging:
    async def send_private_message(self, user_id: str, message: str) -> None:
        raise NotImplementedError

    async def send_channel_message(self, channel_id: str, message: str) -> None:
        raise NotImplementedError
    
    async def wait_for_reaction(self, filter: Optional[Callable[[Reaction], bool]] = None, timeout: int = 60) -> Reaction:
        raise NotImplementedError
