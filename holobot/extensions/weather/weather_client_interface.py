from .models import WeatherData

class WeatherClientInterface:
    async def get_weather_data(self, city_name: str) -> WeatherData:
        raise NotImplementedError
