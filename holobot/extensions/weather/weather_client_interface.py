from .models import WeatherData

class WeatherClientInterface:
    async def get_weather_data(self, location: str) -> WeatherData:
        raise NotImplementedError
