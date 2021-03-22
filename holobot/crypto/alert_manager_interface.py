from decimal import Decimal
from holobot.crypto.enums.frequency_type import FrequencyType
from holobot.crypto.enums.price_direction import PriceDirection
from holobot.crypto.models.alert import Alert
from typing import List

class AlertManagerInterface:
    async def add(self, user_id: str, symbol: str, direction: PriceDirection, value: Decimal,
        frequency_type: FrequencyType = FrequencyType.DAYS, frequency: int = 1):
        raise NotImplementedError

    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> List[Alert]:
        raise NotImplementedError

    async def remove_many(self, user_id: str, symbol: str) -> List[Alert]:
        raise NotImplementedError

    async def remove_all(self, user_id: str) -> List[Alert]:
        raise NotImplementedError
