from datetime import timedelta

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComponentStyle, ContainerLayout, Label, SectionLayout, Separator, Thumbnail
)
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.extensions.weather import IWeatherClient
from holobot.extensions.weather.exceptions import (
    InvalidLocationError, OpenWeatherError, QueryQuotaExhaustedError
)
from holobot.extensions.weather.models import Condition, OpenWeatherOptions, Weather, Wind
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.i18n import localize, localize_random_list_item
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.utils.datetime_utils import utcnow

_WIND_DIRECTIONS_BY_EIGHTH: tuple[str, ...] = ("north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest")

@injectable(IWorkflow)
class GetBasicWeatherWorkflow(WorkflowBase):
    def __init__(
        self,
        options: IOptions[OpenWeatherOptions],
        weather_client: IWeatherClient
    ) -> None:
        super().__init__()
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
                    content=localize(
                        "extensions.weather.get_basic_weather_workflow.no_information_error"
                    )
                )

            return self._reply(components=self.__create_view(weather_data))
        except InvalidLocationError:
            return self._reply(
                content=localize(
                    "extensions.weather.get_basic_weather_workflow.invalid_location_error"
                )
            )
        except OpenWeatherError as error:
            return self._reply(
                content=localize(
                    "extensions.weather.get_basic_weather_workflow.openweather_error",
                    { "code": error.error_code }
                )
            )
        except InvalidOperationError:
            return self._reply(content=localize("feature_disabled_error"))
        except QueryQuotaExhaustedError:
            return self._reply(content=localize("feature_quota_exhausted_error"))
        except CircuitBrokenError:
            return self._reply(content=localize("rate_limit_error"))

    @staticmethod
    def __get_wind_description(data: Weather) -> str:
        if not data.wind:
            return ""

        wind_speed = data.wind.speed or 0
        wind_speed_higher_order = (data.wind.speed or 0) * 3.6
        if data.wind.degrees is None:
            return localize(
                "extensions.weather.get_basic_weather_workflow.wind_no_direction_label",
                {
                    "wind_speed": wind_speed,
                    "wind_speed_higher_order": wind_speed_higher_order
                }
            )

        wind_direction_key = _WIND_DIRECTIONS_BY_EIGHTH[
            int(data.wind.degrees * len(_WIND_DIRECTIONS_BY_EIGHTH) / 360) % len(_WIND_DIRECTIONS_BY_EIGHTH)
        ]
        wind_direction = localize(
            f"extensions.weather.get_basic_weather_workflow.wind_directions.{wind_direction_key}"
        )

        return localize(
            "extensions.weather.get_basic_weather_workflow.wind_label",
            {
                "wind_speed": wind_speed,
                "wind_speed_higher_order": wind_speed_higher_order,
                "wind_direction": wind_direction
            }
        )

    @staticmethod
    def __get_time_description(data: Weather) -> str:
        if data.utc_offset_seconds is None:
            return ""

        local_time = utcnow() + timedelta(seconds=data.utc_offset_seconds)

        return localize(
            "extensions.weather.get_basic_weather_workflow.time_label",
            {
                "local_time": local_time.strftime("%Y.%m.%d. %H:%M:%S")
            }
        )

    def __create_view(self, data: Weather) -> ContainerLayout:
        header = Label(
            id="1_1_1",
            content=localize(
                "extensions.weather.get_basic_weather_workflow.header_label",
                {
                    "name": data.name,
                    "country_flag": data.unicode_country_flag,
                    "quote": localize_random_list_item(
                        "extensions.weather.get_basic_weather_workflow.quotes"
                    )
                }
            )
        )
        wind_description = GetBasicWeatherWorkflow.__get_wind_description(data)
        time_description = GetBasicWeatherWorkflow.__get_time_description(data)
        weather_data = Label(
            id="1_3_1",
            content=localize(
                "extensions.weather.get_basic_weather_workflow.weather_label",
                {
                    "temperature": data.temperature,
                    "temperature_feels_like": data.temperature_feels_like,
                    "humidity": data.humidity,
                    "cloudiness": data.cloudiness,
                    "condition": (
                        data.condition.description
                        if data.condition and data.condition.description
                        else localize("extensions.weather.get_basic_weather_workflow.unknown_condition")
                    ),
                    "wind_info": wind_description,
                    "time_info": time_description
                }
            )
        )

        layout = ContainerLayout(
            id="1",
            accent_color=0xEB7D00,
            children=[
                SectionLayout(
                    id="1_1",
                    children=[header],
                    accessory=Button(
                        id="1_1_0",
                        owner_id=0,
                        text=localize(
                            "extensions.weather.get_basic_weather_workflow.map_button"
                        ),
                        url=self.__options.value.MapUrl.format(
                            latitude=data.latitude,
                            longitude=data.longitude
                        ),
                        style=ComponentStyle.LINK
                    )
                )
                if self.__options.value.MapUrl
                else header,
                Separator(id="1_2"),
                SectionLayout(
                    id="1_3",
                    accessory=Thumbnail(
                        id="1_3_0",
                        media=data.condition.condition_image_url,
                        description=data.condition.description
                    ),
                    children=[weather_data]
                )
                if data.condition and data.condition.condition_image_url
                else weather_data,
                Separator(id="1_4"),
                Label(
                    id="1_5",
                    content=localize(
                        "extensions.weather.get_basic_weather_workflow.footer_label"
                    )
                )
            ]
        )

        return layout
