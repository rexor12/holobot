from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.mudada.models import ExchangeQuota
from holobot.sdk.database.repositories import IRepository

class IExchangeQuotaRepository(IRepository[str, ExchangeQuota], Protocol):
    ...
