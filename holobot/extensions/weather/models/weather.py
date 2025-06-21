from dataclasses import dataclass

from .condition import Condition
from .wind import Wind

UnicodeCodePointLetterA = ord("A")

@dataclass(kw_only=True)
class Weather:
    """Holds information about the weather in a specific location."""

    name: str
    """The name of the location (such as a city)."""

    country_code: str | None
    """ISO-3166 Alpha-2 country code."""

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

    utc_offset_seconds: int | None = None
    """The shift in seconds from the UTC time-zone."""

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

    @property
    def unicode_country_flag(self) -> str:
        if not self.country_code:
            return ""

        # Among the Unicode characters, regional indicators start at 0x1F1E6.
        # For example, this will turn the letters "JP" into "🇯🇵".
        return "".join(
            chr(0x1F1E6 + ord(char.upper()) - UnicodeCodePointLetterA)
            for char in self.country_code
        )

    @staticmethod
    def __celsius_to_fahrenheit(value: float) -> float:
        return (value * 9 / 5) + 32
