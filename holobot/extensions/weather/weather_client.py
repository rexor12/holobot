from json import dumps
from typing import Any

from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from .exceptions import InvalidLocationError, OpenWeatherError, QueryQuotaExhaustedError
from .models import OpenWeatherOptions, WeatherData
from .weather_client_interface import WeatherClientInterface

@injectable(WeatherClientInterface)
class WeatherClient(WeatherClientInterface):
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

    async def get_weather_data(self, location: str) -> WeatherData:
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

        self.__assert_result_code(location, response)

        weather_data = WeatherData.from_json(response)
        self.__set_condition_image(weather_data)
        return weather_data

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

    def __assert_result_code(self, location: str, response: dict[str, Any]) -> None:
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

    def __set_condition_image(self, weather_data: WeatherData) -> None:
        options = self.__options.value
        if (options.ConditionImageBaseUrl is None
            or weather_data.condition.icon is None):
            return
        weather_data.condition.condition_image_url = (
            f"{options.ConditionImageBaseUrl}"
            f"{weather_data.condition.icon}"
            "@2x.png"
        )
