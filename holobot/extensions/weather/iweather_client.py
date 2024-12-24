from collections.abc import Awaitable
from typing import Protocol

from .models import Weather

class IWeatherClient(Protocol):
    def get_weather_data(self, location: str) -> Awaitable[Weather]:
        ...
