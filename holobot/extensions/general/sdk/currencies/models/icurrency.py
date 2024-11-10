from typing import Protocol

class ICurrency(Protocol):
    identifier: int
    """The identifier of the currency."""

    server_id: int | None
    """The identifier of the server the currency belongs to;
    or, None if it's globally available."""

    name: str
    """The displayed name of the currency."""

    description: str | None
    """The displayed description of the currency."""

    emoji_id: int
    """The identifier of the emoji associated to this currency.

    This emoji must be available in the server in which the currency exists.
    If the currency is global, the emoji may come from any server the bot is a member of.
    """

    emoji_name: str
    """The name of the emoji associated to this currency.

    This emoji must be available in the server in which the currency exists.
    If the currency is global, the emoji may come from any server the bot is a member of.
    """
