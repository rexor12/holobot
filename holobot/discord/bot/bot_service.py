from .bot import Bot
from .bot_service_interface import BotServiceInterface
from ..messaging import Messaging
from asyncio.tasks import Task
from discord import Intents
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import CommandObject, SubcommandObject
from holobot.discord.sdk import ExtensionProviderInterface
from holobot.discord.sdk.commands import CommandInterface, CommandExecutionRuleInterface
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, Optional, Tuple, Union

import asyncio, time

DEFAULT_BOT_PREFIX = "h!"
DEBUG_MODE_BOT_PREFIX = "h#"

intents = Intents(
    guilds=True,
    members=True,
    emojis=True,
    voice_states=True,
    guild_messages=True,
    guild_reactions=True
)

@injectable(BotServiceInterface)
class BotService(BotServiceInterface):
    def __init__(self,
        configurator: ConfiguratorInterface,
        extension_providers: Tuple[ExtensionProviderInterface, ...],
        log: LogInterface,
        commands: Tuple[CommandInterface, ...],
        command_execution_rules: Tuple[CommandExecutionRuleInterface, ...],
        debugger: DebuggerInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator
        self.__extension_providers: Tuple[ExtensionProviderInterface, ...] = extension_providers
        self.__log: LogInterface = log.with_name("Discord", "BotService")
        self.__commands: Tuple[CommandInterface, ...] = commands
        self.__command_execution_rules: Tuple[CommandExecutionRuleInterface, ...] = command_execution_rules
        self.__debugger: DebuggerInterface = debugger
        self.__bot: Bot = self.__initialize_bot()
        self.__slash: SlashCommand = SlashCommand(self.__bot, sync_commands=True, sync_on_cog_reload=True, delete_from_unused_guilds=True)
        self.__bot_task: Optional[Task] = None
        # See the reference for a note about what this is.
        Messaging.bot = self.__bot

    async def start(self) -> None:
        if self.__bot_task is not None:
            raise InvalidOperationError("The bot is running already.")

        if not (discord_token := self.__configurator.get("General", "DiscordToken", "")):
            raise ValueError("The Discord token is not configured.")
        
        self.__log.info("Loading extensions...")
        extension_count = 0
        for extension_provider in self.__extension_providers:
            for package in extension_provider.get_packages():
                self.__log.debug(f"Loading extension... {{ Package = {package} }}")
                self.__bot.load_extension(package)
                extension_count += 1
                self.__log.debug(f"Loaded extension. {{ Package = {package} }}")
        self.__log.info(f"Successfully loaded extensions. {{ Count = {extension_count} }}")

        self.__log.info("Registering commands...")
        for command in self.__commands:
            await self.__add_slash_command(command)
            self.__log.debug(f"Registered command. {{ Group = {command.group_name}, SubGroup = {command.subgroup_name}, Name = {command.name} }}")
        self.__log.info(f"Successfully registered commands. {{ Count = {len(self.__commands)} }}")
        
        self.__bot_task = asyncio.get_event_loop().create_task(self.__bot.start(discord_token))

    async def stop(self) -> None:
        if self.__bot_task is None:
            return

        await self.__bot.close()
        await self.__bot_task
        self.__bot_task = None

    async def send_dm(self, user_id: str, message: str) -> None:
        if not (user := self.__bot.get_user_by_id(int(user_id))):
            self.__log.warning(f"Inexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        await user.send(message)

    async def __add_slash_command(self, command: CommandInterface) -> Union[CommandObject, SubcommandObject]:
        command_name = command.name if not self.__debugger.is_debug_mode_enabled() else f"d{command.name}"
        if not command.group_name:
            return self.__slash.add_slash_command(
                lambda context, **kwargs: self.__execute_command(command, context, **kwargs),
                command_name,
                command.description,
                list(await command.get_allowed_guild_ids()),
                command.options
            )

        return self.__slash.add_subcommand(
            lambda context, **kwargs: self.__execute_command(command, context, **kwargs),
            command.group_name,
            command.subgroup_name,
            command_name,
            command.description,
            guild_ids=list(await command.get_allowed_guild_ids()),
            options=command.options
        )

    async def __execute_command(self, __command: CommandInterface, context: SlashContext, **kwargs: Any) -> None:
        self.__log.trace(f"Executing command... {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id} }}")
        start_time = time.perf_counter()
        await context.defer()
        for rule in self.__command_execution_rules:
            if await rule.should_halt(__command, context):
                self.__log.debug(f"Command has been halted. {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id} }}")
                await reply(context, "You're not allowed to use this command here.")
                return

        await __command.execute(context, **kwargs)
        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Executed command. {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id}, Elapsed = {elapsed_time} }}")

    def __initialize_bot(self) -> Bot:
        bot = Bot(
            self.__log,
            # TODO Guild-specific custom prefix.
            command_prefix = DEFAULT_BOT_PREFIX if not self.__configurator.get("General", "IsDebug", False) else DEBUG_MODE_BOT_PREFIX,
            case_insensitive = True,
            intents = intents,
            loop = asyncio.get_event_loop()
        )

        bot.add_listener(self.__on_slash_command_error, "on_slash_command_error")

        return bot

    async def __on_slash_command_error(self, context: SlashContext, exception: Exception) -> None:
        self.__log.error((
            "An error has occurred while processing a slash command. "
            f"{{ Type = {type(exception).__name__}, UserId = {get_author_id(context)} }}"
            ), exception)
