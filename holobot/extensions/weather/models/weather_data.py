from .condition_data import ConditionData
from holobot.sdk.utils import try_parse_float, try_parse_int
from typing import Any, Dict, Optional

class WeatherData:
    def __init__(self) -> None:
        self.name = ""
        self.temperature = None
        self.temperature_feels_like = None
        self.pressure = None
        self.humidity = None
        self.condition = ConditionData()

    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    # °C, if requested metric
    @property
    def temperature(self) -> Optional[float]:
        return self.__temperature
    
    @temperature.setter
    def temperature(self, value: Optional[float]) -> None:
        self.__temperature = value
    
    # °C, if requested metric
    @property
    def temperature_feels_like(self) -> Optional[float]:
        return self.__temperature_feels_like
    
    @temperature_feels_like.setter
    def temperature_feels_like(self, value: Optional[float]) -> None:
        self.__temperature_feels_like = value
    
    # hPa
    @property
    def pressure(self) -> Optional[int]:
        return self.__pressure
    
    @pressure.setter
    def pressure(self, value: Optional[int]) -> None:
        self.__pressure = value
    
    # Percentage.
    @property
    def humidity(self) -> Optional[int]:
        return self.__humidity
    
    @humidity.setter
    def humidity(self, value: Optional[int]) -> None:
        self.__humidity = value
    
    @property
    def condition(self) -> ConditionData:
        return self.__condition

    @condition.setter
    def condition(self, value: ConditionData) -> None:
        self.__condition = value
    
    @staticmethod
    def from_json(json: Dict[str, Any]) -> 'WeatherData':
        entity = WeatherData()
        entity.name = json.get("name", "Unknown")
        WeatherData.fill_main_data(entity, json.get("main", {}))
        entity.condition = ConditionData.from_json(json.get("weather", [])[0]) # Using the primary condition only.
        return entity
    
    @staticmethod
    def fill_main_data(weather_data: 'WeatherData', json: Dict[str, Any]) -> None:
        weather_data.temperature = try_parse_float(json.get("temp", None))
        weather_data.temperature_feels_like = try_parse_float(json.get("feels_like", None))
        weather_data.pressure = try_parse_int(json.get("pressure", None))
        weather_data.humidity = try_parse_int(json.get("humidity", None))
