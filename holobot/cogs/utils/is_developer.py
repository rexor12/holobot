from discord.ext.commands import Context
from holobot.exceptions.authorization_error import AuthorizationError
from holobot.security.credential_manager_interface import CredentialManagerInterface
from typing import Callable, Optional

import functools

def is_developer(wrapped_func = None):
    def decorator(wrapped_func):
        @functools.wraps(wrapped_func)
        async def wrapper(self, context: Context, *args, **kwargs):
            credential_manager = __find_credential_manager(self)
            if not credential_manager:
                raise TypeError("The class the decorated function belongs to holds no attribute of type CredentialManagerInterface.")
            if not (dev_ids := credential_manager.get("developer_user_ids")):
                raise AuthorizationError(context.author.id)

            dev_ids_split = [int(dev_id) for dev_id in dev_ids.split(",")]
            if not context.author.id in dev_ids_split:
                raise AuthorizationError(context.author.id)

            await wrapped_func(self, context, *args, **kwargs)
        return wrapper
    
    # @is_developer
    if wrapped_func is not None and isinstance(wrapped_func, Callable):
        return decorator(wrapped_func)

    # @is_developer()
    return decorator

def __find_credential_manager(instance) -> Optional[CredentialManagerInterface]:
    for value in instance.__dict__.values():
        if isinstance(value, CredentialManagerInterface):
            return value