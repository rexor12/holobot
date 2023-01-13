from typing import Any

from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.serialization.json_serializer import deserialize
from .dtos.weather_data import WeatherData
from .exceptions import InvalidLocationError, OpenWeatherError, QueryQuotaExhaustedError
from .iweather_client import IWeatherClient
from .models import Condition, OpenWeatherOptions, Weather, Wind

@injectable(IWeatherClient)
class WeatherClient(IWeatherClient):
    def __init__(
        self,
        http_client_pool: IHttpClientPool,
        logger_factory: ILoggerFactory,
        options: IOptions[OpenWeatherOptions]
    ) -> None:
        super().__init__()
        self.__http_client_pool: IHttpClientPool = http_client_pool
        self.__logger = logger_factory.create(WeatherClient)
        self.__options = options
        self.__circuit_breaker: AsyncCircuitBreakerPolicy = WeatherClient.__create_circuit_breaker(options.value)
        # TODO Caching with configurable time based expiry.
        #self.__cache: ConcurrentCache[str, int | None] = ConcurrentCache()

    async def get_weather_data(self, location: str) -> Weather:
        options = self.__options.value
        if not options.ApiKey:
            raise InvalidOperationError("OpenWeather isn't configured.")
        if not location:
            raise ValueError("The city name must be specified.")

        try:
            response = await self.__circuit_breaker(
                lambda s: self.__http_client_pool.get(s[0], s[1]),
                (
                    options.ApiGatewayBaseUrl,
                    {
                        "appid": options.ApiKey,
                        "q": location,
                        "units": "metric"
                    }
                )
            )
        except TooManyRequestsError:
            raise QueryQuotaExhaustedError
        except HttpStatusError as error:
            self.__logger.error("An HTTP error has occurred during an OpenWeather request", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__logger.error("An unexpected error has occurred during an OpenWeather request", error)
            raise

        return self.__dto_to_model(self.__deserialize_result(location, response))

    @staticmethod
    def __create_circuit_breaker(
        options: OpenWeatherOptions
    ) -> AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any]:
        return AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any](
            options.CircuitBreakerFailureThreshold,
            options.CircuitBreakerRecoveryTime,
            WeatherClient.__on_circuit_broken
        )

    @staticmethod
    async def __on_circuit_broken(
        circuit_breaker: AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any],
        error: Exception
    ) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)):
            return error.retry_after
        return circuit_breaker.recovery_timeout

    def __deserialize_result(self, location: str, response: dict[str, Any]) -> WeatherData:
        result_code = response.get("cod")
        if result_code is None:
            # self.__logger.trace(dumps(response))
            self.__logger.error("Received a response with no result code", location=location)
            raise OpenWeatherError("N/A", location)
        result_code = str(result_code)
        if result_code == "404":
            raise InvalidLocationError(location)
        if result_code != "200":
            # self.__logger.trace(dumps(response))
            self.__logger.warning(
                "Received a response with an unexpected non-success code",
                code=result_code,
                location=location
            )
            raise OpenWeatherError(result_code, location)

        weather_data = deserialize(WeatherData, response)
        if not weather_data:
            raise InvalidLocationError(location)

        return weather_data

    def __dto_to_model(self, dto: WeatherData) -> Weather:
        options = self.__options.value

        return Weather(
            name=dto.name,
            longitude=dto.coord.lon,
            latitude=dto.coord.lat,
            temperature=dto.main.temp,
            temperature_feels_like=dto.main.feels_like or dto.main.temp,
            humidity=dto.main.humidity,
            cloudiness=dto.clouds.all,
            condition=(
                Condition(
                    identifier=dto.weather[0].id,
                    icon=dto.weather[0].icon,
                    condition_image_url=(
                        f"{options.ConditionImageBaseUrl}"
                        f"{dto.weather[0].icon}"
                        "@2x.png"
                    )
                    if options.ConditionImageBaseUrl and dto.weather[0].icon
                    else None,
                    description=dto.weather[0].description or dto.weather[0].main
                )
            ) if dto.weather else None,
            wind=(
                Wind(
                    speed=dto.wind.speed,
                    degrees=dto.wind.deg
                )
                if dto.wind
                else None
            )
        )
