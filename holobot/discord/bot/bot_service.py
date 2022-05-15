from .bot_accessor import BotAccessor
from .bot import Bot
from .bot_service_interface import BotServiceInterface
from .ibot_event_handler import IBotEventHandler
from ..commands import ICommandProcessor
from ..components import IComponentInteractionProcessor
from ..context_menus import IMenuItemRegistry
from asyncio.tasks import Task
from discord import Intents
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_choice, create_option, SlashCommandOptionType
from holobot.discord.sdk import ExtensionProviderInterface
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import Option
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, Dict, List, Optional, Tuple

import asyncio

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
        command_processor: ICommandProcessor,
        commands: Tuple[CommandInterface, ...],
        debugger: DebuggerInterface,
        context_menu_item_registry: IMenuItemRegistry,
        component_interaction_processor: IComponentInteractionProcessor,
        bot_event_handler: IBotEventHandler) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator
        self.__extension_providers: Tuple[ExtensionProviderInterface, ...] = extension_providers
        self.__log: LogInterface = log.with_name("Discord", "BotService")
        self.__command_processor: ICommandProcessor = command_processor
        self.__commands: Tuple[CommandInterface, ...] = commands
        self.__debugger: DebuggerInterface = debugger
        self.__context_menu_item_registry: IMenuItemRegistry = context_menu_item_registry
        self.__component_interaction_processor: IComponentInteractionProcessor = component_interaction_processor
        self.__bot_event_handler: IBotEventHandler = bot_event_handler
        self.__bot: Bot = self.__initialize_bot()
        self.__slash: SlashCommand = SlashCommand(self.__bot, sync_commands=False, sync_on_cog_reload=False, delete_from_unused_guilds=False)
        self.__bot_task: Optional[Task] = None
        # See the reference for a note about what this is.
        BotAccessor._bot = self.__bot

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
            await self.__register_command(command)
            self.__log.debug(f"Registered command. {{ Group = {command.group_name}, SubGroup = {command.subgroup_name}, Name = {command.name} }}")
        self.__log.info(f"Successfully registered commands. {{ Count = {len(self.__commands)} }}")

        self.__context_menu_item_registry.register_menu_items(self.__slash)
        
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
    
    @staticmethod
    def __get_option_type(option_type: OptionType) -> SlashCommandOptionType:
        if option_type == OptionType.BOOLEAN:
            return SlashCommandOptionType.BOOLEAN
        if option_type == OptionType.INTEGER:
            return SlashCommandOptionType.INTEGER
        if option_type == OptionType.FLOAT:
            return SlashCommandOptionType.FLOAT
        return SlashCommandOptionType.STRING

    @staticmethod
    def __transform_options(options: List[Option]) -> List[Dict[str, Any]]:
        result = []
        for option in options:
            result.append(create_option(
                option.name,
                option.description,
                BotService.__get_option_type(option.type),
                option.is_mandatory,
                [create_choice(choice.value, choice.name) for choice in option.choices]
            ))
        return result

    async def __register_command(self, command: CommandInterface) -> None:
        command_name = command.name if not self.__debugger.is_debug_mode_enabled() else f"d{command.name}"
        if not command.group_name:
            await self.__add_slash_command(command, command_name)
        else: await self.__add_slash_subcommand(command, command_name)

        for component in command.components:
            # No type error here, the type hint is wrong in the library.
            self.__slash.add_component_callback(
                lambda context, __c=component: self.__component_interaction_processor.process(__c, context), # type: ignore
                components=component.id)

    async def __add_slash_command(self, command: CommandInterface, command_name: str) -> None:
        self.__slash.add_slash_command(
            lambda context, **kwargs: self.__command_processor.process(command, context, **kwargs),
            command_name,
            command.description,
            list(await command.get_allowed_guild_ids()),
            BotService.__transform_options(command.options)
        )

    async def __add_slash_subcommand(self, command: CommandInterface, command_name: str) -> None:
        self.__slash.add_subcommand(
            lambda context, **kwargs: self.__command_processor.process(command, context, **kwargs),
            command.group_name,
            command.subgroup_name,
            command_name,
            command.description,
            guild_ids=list(await command.get_allowed_guild_ids()),
            options=BotService.__transform_options(command.options)
        )

    def __initialize_bot(self) -> Bot:
        bot = Bot(
            self.__log,
            # TODO Guild-specific custom prefix.
            command_prefix = DEFAULT_BOT_PREFIX if not self.__configurator.get("General", "IsDebug", False) else DEBUG_MODE_BOT_PREFIX,
            case_insensitive = True,
            intents = intents,
            loop = asyncio.get_event_loop()
        )
        
        self.__bot_event_handler.register_callbacks(bot)

        return bot
