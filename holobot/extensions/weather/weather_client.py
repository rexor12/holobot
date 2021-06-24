from .exceptions import QueryQuotaExhaustedError
from .models import WeatherData
from .weather_client_interface import WeatherClientInterface
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreaker

CONFIG_SECTION = "OpenWeather"
API_GATEWAY_PARAMETER = "ApiGatewayBaseUrl"
API_KEY_PARAMETER = "ApiKey"
CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER = "CircuitBreakerFailureThreshold"
CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER = "CircuitBreakerRecoveryTime"
CONDITION_IMAGE_BASE_URL_PARAMETER = "ConditionImageBaseUrl"

@injectable(WeatherClientInterface)
class WeatherClient(WeatherClientInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = services.get(ConfiguratorInterface)
        self.__http_client_pool: HttpClientPoolInterface = services.get(HttpClientPoolInterface)
        self.__log: LogInterface = services.get(LogInterface).with_name("Weather", "WeatherClient")
        self.__api_gateway: str = self.__configurator.get(CONFIG_SECTION, API_GATEWAY_PARAMETER, "")
        self.__api_key: str = self.__configurator.get(CONFIG_SECTION, API_KEY_PARAMETER, "")
        self.__condition_image_base_url: str = self.__configurator.get(CONFIG_SECTION, CONDITION_IMAGE_BASE_URL_PARAMETER, "")
        self.__circuit_breaker: AsyncCircuitBreaker = WeatherClient.__create_circuit_breaker(self.__configurator)
        # TODO Caching with configurable time based expiry.
        #self.__cache: ConcurrentCache[str, Optional[int]] = ConcurrentCache()
    
    async def get_weather_data(self, city_name: str) -> WeatherData:
        if not self.__api_key:
            raise InvalidOperationError("OpenWeather isn't configured.")
        if not city_name:
            raise ValueError("The city name must be specified.")
        
        try:
            response = await self.__circuit_breaker(
                self.__http_client_pool.get,
                self.__api_gateway,
                {
                    "appid": self.__api_key,
                    "q": city_name,
                    "units": "metric"
                })
        except TooManyRequestsError:
            raise QueryQuotaExhaustedError
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during an OpenWeather request.", error)
            raise
        except Exception as error:
            self.__log.error(f"An unexpected error has occurred during an OpenWeather request. ({type(error)})", error)
            raise
        
        weather_data = WeatherData.from_json(response)
        self.__set_condition_image(weather_data)
        return weather_data
    
    @staticmethod
    def __create_circuit_breaker(configurator: ConfiguratorInterface) -> AsyncCircuitBreaker:
        return AsyncCircuitBreaker(
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER, 1),
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER, 300),
            WeatherClient.__on_circuit_broken)
    
    @staticmethod
    async def __on_circuit_broken(circuit_breaker: AsyncCircuitBreaker, error: Exception) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)):
            return error.retry_after
        return circuit_breaker.recovery_timeout
    
    def __set_condition_image(self, weather_data: WeatherData) -> None:
        if (self.__condition_image_base_url is None
            or weather_data.condition.icon is None):
            return
        weather_data.condition.condition_image_url = (
            f"{self.__condition_image_base_url}"
            f"{weather_data.condition.icon}"
            "@2x.png"
        )
