from .bot import Bot

# NOTE: This is a hack, because we have a circular dependency here.
# Some services need the Bot instance, which services are typically used by commands,
# which commands are used by the Bot instance.
# Therefore, as a hack, we're using this static field
# to have a reference to our instance of Bot... at some point.
# To avoid this, kanata needs to support lazy dependency injection.
_bot: Bot | None = None

def get_bot() -> Bot:
    if _bot is None:
        raise ValueError("The bot instance hasn't been initialized.")

    return _bot
