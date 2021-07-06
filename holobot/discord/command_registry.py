from .sdk.commands import CommandDescriptor, CommandRegistryInterface
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import assert_not_none
from typing import Optional

@injectable(CommandRegistryInterface)
class CommandRegistry(CommandRegistryInterface):
    # As usual for class variables in this project, this is a hack
    # needed because of discord.py, to register commands using a
    # decorator. A proper solution would be to make each command an
    # injectable and they would register themselves through an
    # instance of this class. This is, however, not possible because
    # discord.py uses black magic to register the decorated commands.
    global_registry: ConcurrentCache[str, CommandDescriptor] = ConcurrentCache()

    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__log: LogInterface = services.get(LogInterface).with_name("Discord", "CommandRegistry")
        self.__registry: ConcurrentCache[str, CommandDescriptor] = ConcurrentCache()
        # Without the hack above, this would be a good place to register the commands.
    
    @staticmethod
    async def register_global(command: CommandDescriptor) -> None:
        assert_not_none(command, "command")
        await CommandRegistry.global_registry.add_or_update_sync(
            CommandRegistry.__get_key_for(command),
            lambda key: command,
            lambda key, previous: command
        )

    async def register(self, command: CommandDescriptor) -> None:
        assert_not_none(command, "command")
        await self.__registry.add_or_update_sync(
            CommandRegistry.__get_key_for(command),
            lambda key: command,
            lambda key, previous: command
        )
        self.__log.debug(f"Registered command. {{ Group = {command.group}, SubGroup = {command.sub_group}, Name = {command.name} }}")
    
    async def command_exists(self, name: str, group: Optional[str] = None, sub_group: Optional[str] = None) -> bool:
        return await self.__registry.contains_key(CommandRegistry.__get_key(name, group, sub_group))
    
    async def group_exists(self, group: str) -> bool:
        return await self.__registry.contains_key(CommandRegistry.__get_key(None, group, None))
    
    @staticmethod
    def __get_key_for(command: CommandDescriptor) -> str:
        return CommandRegistry.__get_key(command.name, command.group, command.sub_group)
    
    @staticmethod
    def __get_key(name: Optional[str], group: Optional[str], sub_group: Optional[str]) -> str:
        return f"{group}-{sub_group}-{name}"
