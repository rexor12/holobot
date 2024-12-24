from dataclasses import dataclass

from .item_base import ItemBase

@dataclass
class CurrencyItem(ItemBase):
    """A currency type item."""

    currency_id: int
    """The identifier of the currency.

    This should be interpreted within a server context.
    """
