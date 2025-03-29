from dataclasses import dataclass

from holobot.extensions.general.enums import GrantItemOutcome
from holobot.extensions.general.models.items import UserItem
from holobot.extensions.general.sdk.wallets.models import ExchangeInfo

@dataclass(kw_only=True)
class TransactionInfo:
    outcome: GrantItemOutcome
    item: UserItem
    item_count: int
    exchange_info: ExchangeInfo | None = None
