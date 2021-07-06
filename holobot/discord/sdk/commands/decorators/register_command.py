from discord_slash.context import SlashContext
from discord_slash.model import CogCommandObject, CogSubcommandObject
from holobot.discord import CommandRegistry
from holobot.discord.sdk.commands import CommandDescriptor
from typing import Callable

import asyncio
import functools

def register_command(wrapped_func = None):
    def decorator(wrapped_func):
        # Another beautiful hack. See the called method for details.
        asyncio.get_event_loop().run_until_complete(
            CommandRegistry.register_global(__get_command_descriptor(wrapped_func)))

        # @functools.wraps(wrapped_func)
        # async def wrapper(self, context: SlashContext, *args, **kwargs):
        #     await __invoke_command(wrapped_func, self, context, *args, **kwargs)
        # return wrapper
        return wrapped_func
    
    # @register_command
    if wrapped_func is not None and isinstance(wrapped_func, Callable):
        return decorator(wrapped_func)

    # @register_command()
    return decorator

def __get_command_descriptor(wrapped_func) -> CommandDescriptor:
    if isinstance(wrapped_func, CogSubcommandObject):
        return CommandDescriptor(wrapped_func.name, wrapped_func.base, wrapped_func.subcommand_group)
    if isinstance(wrapped_func, CogCommandObject):
        return CommandDescriptor(wrapped_func.name)
    raise TypeError(f"The command type '{type(wrapped_func)}' is not supported.")

async def __invoke_command(wrapped_func, instance, context: SlashContext, *args, **kwargs):
    # TODO Determine if the command can be invoked depending on command rules.
    await wrapped_func(instance, context, *args, **kwargs)
