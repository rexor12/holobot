from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class ExchangeQuota(AggregateRoot[int]):
    """Represents a Mudada exchange quota."""

    amount: int
    """The amount of the currency the user has exchanged
    within the current quota.

    This value may not necessarily reflect the total amount
    of currency the user has exchanged, as it can be reset/changed
    by moderators.
    """

    exchanged_amount: int
    """The amount of the currency the user has exchanged."""

    lost_amount: int
    """The amount of the currency the user has lost in total.

    This typically happens when the user goes above the quota,
    because Holo has no way to refuse gifts.
    """
