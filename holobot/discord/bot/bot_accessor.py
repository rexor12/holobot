from .bot import Bot
from typing import Optional

class BotAccessor:
    # NOTE: This is a hack, because we have a circular dependency here.
    # Some services need the Bot instance, which services are typically used by commands,
    # which commands are used by the Bot instance.
    # Therefore, as a hack, we're using this static field
    # to have a reference to our instance of Bot... at some point.
    # This could possibly be avoided if discord.py supported IoC, which it doesn't.
    _bot: Optional[Bot] = None

    def __init__(self) -> None:
        raise TypeError("Cannot initialize instances of this static type.")

    @staticmethod
    def get_bot() -> Bot:
        bot = BotAccessor._bot
        if bot is None:
            raise ValueError("The bot instance hasn't been initialized.")

        return bot
