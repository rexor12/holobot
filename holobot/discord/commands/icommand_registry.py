from ..bot import Bot
from abc import ABCMeta, abstractmethod
from hikari.api.special_endpoints import SlashCommandBuilder
from holobot.discord.sdk.commands import CommandInterface
from typing import Optional, Sequence

class ICommandRegistry(metaclass=ABCMeta):
    @abstractmethod
    def get_command(self, group_name: Optional[str], sub_group_name: Optional[str], name: str) -> Optional[CommandInterface]:
        ...

    @abstractmethod
    def get_command_builders(self, bot: Bot) -> Sequence[SlashCommandBuilder]:
        ...
