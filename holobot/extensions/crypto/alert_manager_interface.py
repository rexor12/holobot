from decimal import Decimal
from typing import List, Protocol

from .enums import FrequencyType, PriceDirection
from .models import Alert
from holobot.sdk.queries import PaginationResult

class AlertManagerInterface(Protocol):
    async def add(self, user_id: str, symbol: str, direction: PriceDirection, value: Decimal,
        frequency_type: FrequencyType = FrequencyType.DAYS, frequency: int = 1):
        ...

    async def get_many(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> PaginationResult[Alert]:
        ...

    async def remove_many(self, user_id: str, symbol: str) -> List[Alert]:
        ...

    async def remove_all(self, user_id: str) -> List[Alert]:
        ...
