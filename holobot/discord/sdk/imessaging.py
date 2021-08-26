from .models import Embed, InteractionContext, Message, Reaction
from typing import Callable, Optional, Union

class IMessaging:
    async def send_private_message(self, user_id: str, message: str) -> None:
        raise NotImplementedError

    async def send_channel_message(self, channel_id: str, message: str) -> None:
        raise NotImplementedError
    
    async def wait_for_reaction(self, filter: Optional[Callable[[Reaction], bool]] = None, timeout: int = 60) -> Reaction:
        raise NotImplementedError

    async def add_reaction(self, context: InteractionContext, message: Message, emoji: str) -> None:
        raise NotImplementedError

    async def remove_reaction(self, context: InteractionContext, message: Message, owner_id: str, emoji: str) -> None:
        raise NotImplementedError

    async def edit_message(self, context: InteractionContext, message: Message, content: Union[str, Embed]) -> None:
        raise NotImplementedError

    async def send_reply(self, context: InteractionContext, message: Message, content: Union[str, Embed]) -> Message:
        raise NotImplementedError

    async def send_context_reply(self, context: InteractionContext, content: Union[str, Embed]) -> Message:
        raise NotImplementedError

    async def delete_message(self, context: InteractionContext, message: Message) -> None:
        raise NotImplementedError
