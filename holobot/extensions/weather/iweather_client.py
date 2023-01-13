from .models import Weather

class IWeatherClient:
    async def get_weather_data(self, location: str) -> Weather:
        raise NotImplementedError
