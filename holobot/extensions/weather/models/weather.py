from dataclasses import dataclass

from .condition import Condition
from .wind import Wind

@dataclass(kw_only=True)
class Weather:
    """Holds information about the weather in a specific location."""

    name: str
    """The name of the location (such as a city)."""

    latitude: float
    """The longitude of the location's coordinates."""

    longitude: float
    """The latitude of the location's coordinates."""

    temperature: float | None
    """The current temperature, in Celsius."""

    temperature_feels_like: float | None
    """How the current temperature feels, in Celsius."""

    humidity: float | None
    """The humidity percentage."""

    cloudiness: float | None
    """The percentage of cloudiness."""

    condition: Condition | None = None
    """Information about the currently dominant weather condition."""

    wind: Wind | None = None
    """Information about the wind."""

    @property
    def temperature_fahrenheit(self) -> float | None:
        """Calculates the temperature in Fahrenheit.

        :return: The temperature in Fahrenheit.
        :rtype: float
        """

        return (
            Weather.__celsius_to_fahrenheit(self.temperature)
            if self.temperature
            else None
        )

    @property
    def temperature_feels_like_fahrenheit(self) -> float | None:
        """Calculates how teh current temperature feels in Fahrenheit.

        :return: How the current temperatures feels in Fahrenheit.
        :rtype: float
        """

        return (
            Weather.__celsius_to_fahrenheit(self.temperature_feels_like)
            if self.temperature_feels_like
            else None
        )

    @staticmethod
    def __celsius_to_fahrenheit(value: float) -> float:
        return (value * 9 / 5) + 32
