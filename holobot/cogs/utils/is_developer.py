from discord.ext.commands import Context
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import AuthorizationError
from typing import Callable, Optional

import functools

def is_developer(wrapped_func = None):
    def decorator(wrapped_func):
        @functools.wraps(wrapped_func)
        async def wrapper(self, context: Context, *args, **kwargs):
            if not (configurator := __find_configurator(self)):
                raise TypeError("The class the decorated function belongs to holds no attribute of type CredentialManagerInterface.")
            dev_ids = configurator.get("Development", "DeveloperUserIds", [])
            if not str(context.author.id) in dev_ids:
                raise AuthorizationError(context.author.id)

            await wrapped_func(self, context, *args, **kwargs)
        return wrapper
    
    # @is_developer
    if wrapped_func is not None and isinstance(wrapped_func, Callable):
        return decorator(wrapped_func)

    # @is_developer()
    return decorator

def __find_configurator(instance) -> Optional[ConfiguratorInterface]:
    for value in instance.__dict__.values():
        if isinstance(value, ConfiguratorInterface):
            return value