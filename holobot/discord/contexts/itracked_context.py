from abc import abstractmethod
from discord import Message
from discord.ext.commands import Context
from discord_slash.context import ComponentContext, MenuContext, SlashContext
from typing import Awaitable, Callable, Optional, Union
from uuid import UUID

class ITrackedContext:
    @property
    @abstractmethod
    def request_id(self) -> UUID:
        raise NotImplementedError

    @property
    @abstractmethod
    def context(self) -> Union[ComponentContext, Context, MenuContext, SlashContext]:
        raise NotImplementedError

    @abstractmethod
    async def add_message(self, channel_id: str, message_id: str, message: Message) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_message(self, channel_id: str, message_id: str) -> Optional[Message]:
        raise NotImplementedError

    @abstractmethod
    async def get_or_add_message(self, channel_id: str, message_id: str, factory: Callable[[str, str], Awaitable[Message]]) -> Message:
        raise NotImplementedError
