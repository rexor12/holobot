from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.extensions.weather import IWeatherClient
from holobot.extensions.weather.exceptions import (
    InvalidLocationError, OpenWeatherError, QueryQuotaExhaustedError
)
from holobot.extensions.weather.models import OpenWeatherOptions, Weather
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError

_WIND_DIRECTIONS_BY_EIGHTH: tuple[str, ...] = ("north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest")

@injectable(IWorkflow)
class GetBasicWeatherWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        options: IOptions[OpenWeatherOptions],
        weather_client: IWeatherClient
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__options = options
        self.__weather_client = weather_client

    @command(
        description="Displays the current temperature in a city.",
        name="weather",
        options=(
            Option("city", "The name of the city"),
        )
    )
    async def show_basic_weather_info(
        self,
        context: InteractionContext,
        city: str
    ) -> InteractionResponse:
        try:
            weather_data = await self.__weather_client.get_weather_data(city)
            if weather_data.temperature is None:
                return self._reply(
                    content=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.no_information_error"
                    )
                )

            return self._reply(
                embed=self.__create_embed(weather_data),
                components=Button(
                    id="gmaps_link",
                    owner_id=context.author_id,
                    text=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.map_button"
                    ),
                    url=self.__options.value.MapUrl.format(
                        latitude=weather_data.latitude,
                        longitude=weather_data.longitude
                    ),
                    style=ComponentStyle.LINK
                ) if self.__options.value.MapUrl else None
            )
        except InvalidLocationError:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.weather.get_basic_weather_workflow.invalid_location_error"
                )
            )
        except OpenWeatherError as error:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.weather.get_basic_weather_workflow.openweather_error",
                    { "code": error.error_code }
                )
            )
        except InvalidOperationError:
            return self._reply(content=self.__i18n_provider.get("feature_disabled_error"))
        except QueryQuotaExhaustedError:
            return self._reply(content=self.__i18n_provider.get("feature_quota_exhausted_error"))
        except CircuitBrokenError:
            return self._reply(content=self.__i18n_provider.get("rate_limit_error"))

    def __create_embed(self, weather: Weather) -> Embed:
        if weather.wind and weather.wind.degrees is not None:
            wind_direction_key = _WIND_DIRECTIONS_BY_EIGHTH[
                int(weather.wind.degrees * len(_WIND_DIRECTIONS_BY_EIGHTH) / 360)
            ]
            wind_direction = self.__i18n_provider.get(
                f"extensions.weather.get_basic_weather_workflow.wind_directions.{wind_direction_key}"
            )
            wind_value = self.__i18n_provider.get(
                "extensions.weather.get_basic_weather_workflow.embed_field_wind_value",
                {
                    "speed": weather.wind.speed,
                    "direction": wind_direction
                }
            )
        elif weather.wind:
            wind_value = self.__i18n_provider.get(
                "extensions.weather.get_basic_weather_workflow.embed_field_wind_no_degrees_value",
                { "speed": weather.wind.speed }
            )
        else:
            wind_value = "N/A"

        embed = Embed(
            title=self.__i18n_provider.get(
                "extensions.weather.get_basic_weather_workflow.embed_title"
            ),
            description=self.__i18n_provider.get(
                "extensions.weather.get_basic_weather_workflow.embed_description",
                { "location": weather.name }
            ),
            footer=EmbedFooter(
                text=self.__i18n_provider.get(
                    "extensions.weather.get_basic_weather_workflow.embed_footer"
                ),
                icon_url=self.__options.value.IconUrl
            ),
            fields=[
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_temperature"
                    ),
                    value=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_temperature_value",
                        {
                            "temperature": (
                                f"{weather.temperature:,.2f}"
                                if weather.temperature is not None
                                else "N/A"
                            ),
                            "temperature_fahrenheit": (
                                f"{weather.temperature_fahrenheit:,.2f}"
                                if weather.temperature is not None
                                else "N/A"
                            )
                        }
                    )
                ),
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_temperature_feels"
                    ),
                    value=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_temperature_feels_value",
                        {
                            "temperature": (
                                f"{weather.temperature_feels_like:,.2f}"
                                if weather.temperature_feels_like is not None
                                else "N/A"
                            ),
                            "temperature_fahrenheit": (
                                f"{weather.temperature_feels_like_fahrenheit:,.2f}"
                                if weather.temperature_feels_like is not None
                                else "N/A"
                            )
                        }
                    )
                ),
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_humidity"
                    ),
                    value=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_humidity_value",
                        {
                            "humidity": (
                                str(weather.humidity)
                                if weather.humidity is not None
                                else "N/A"
                            )
                        }
                    )
                ),
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_condition"
                    ),
                    value=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_condition_value",
                        {
                            "description": (
                                weather.condition.description
                                if weather.condition and weather.condition.description
                                else "N/A"
                            )
                        }
                    )
                ),
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_wind"
                    ),
                    value=wind_value
                ),
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.embed_field_cloudiness"
                    ),
                    value=(
                        self.__i18n_provider.get(
                            "extensions.weather.get_basic_weather_workflow.embed_field_cloudiness_value",
                            { "cloudiness": int(weather.cloudiness) }
                        )
                        if weather.cloudiness is not None
                        else "N/A"
                    )
                )
            ]
        )

        if weather.condition and weather.condition.condition_image_url:
            embed.thumbnail_url = weather.condition.condition_image_url

        return embed
