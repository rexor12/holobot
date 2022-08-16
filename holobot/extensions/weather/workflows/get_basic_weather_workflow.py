from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from .. import WeatherClientInterface
from ..exceptions import InvalidLocationError, OpenWeatherError, QueryQuotaExhaustedError
from ..models import WeatherData

@injectable(IWorkflow)
class GetBasicWeatherWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        weather_client: WeatherClientInterface
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__weather_client = weather_client
    
    @command(
        description="Displays the current temperature in a city.",
        name="basic",
        group_name="weather",
        options=(
            Option("city", "The name of the city"),
        )
    )
    async def show_basic_weather_info(
        self,
        context: ServerChatInteractionContext,
        city: str
    ) -> InteractionResponse:
        try:
            weather_data = await self.__weather_client.get_weather_data(city)
            if weather_data.temperature is None:
                return InteractionResponse(
                    action=ReplyAction(content=self.__i18n_provider.get(
                        "extensions.weather.get_basic_weather_workflow.no_information_error"
                    ))
                )
            return InteractionResponse(
                action=ReplyAction(content=self.__create_embed(weather_data))
            )
        except InvalidLocationError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.weather.get_basic_weather_workflow.invalid_location_error"
                ))
            )
        except OpenWeatherError as error:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.weather.get_basic_weather_workflow.openweather_error",
                    { "code": error.error_code }
                ))
            )
        except InvalidOperationError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("feature_disabled_error"))
            )
        except QueryQuotaExhaustedError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "feature_quota_exhausted_error"
                ))
            )
        except CircuitBrokenError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("rate_limit_error"))
            )
    
    def __create_embed(self, weather_data: WeatherData) -> Embed:
        embed = Embed(
            title=self.__i18n_provider.get(
                "extensions.eather.get_basic_weather_workflow.embed_title"
            ),
            description=self.__i18n_provider.get(
                "extensions.eather.get_basic_weather_workflow.embed_description",
                { "location": weather_data.name }
            ),
            footer=EmbedFooter(
                text=self.__i18n_provider.get(
                "extensions.eather.get_basic_weather_workflow.embed_footer"
            ),
                icon_url="https://openweathermap.org/themes/openweathermap/assets/img/mobile_app/android_icon.png")
        )
        embed.fields.append(EmbedField(
            name=self.__i18n_provider.get(
                "extensions.eather.get_basic_weather_workflow.embed_field_temperature"
            ),
            value=self.__i18n_provider.get(
                "extensions.eather.get_basic_weather_workflow.embed_field_temperature_value",
                { "temperature": f"{weather_data.temperature:,.2f}" }
            )
        ))

        if weather_data.pressure is not None:
            embed.fields.append(EmbedField(
                name=self.__i18n_provider.get(
                    "extensions.eather.get_basic_weather_workflow.embed_field_pressure"
                ),
                value=self.__i18n_provider.get(
                    "extensions.eather.get_basic_weather_workflow.embed_field_pressure_value",
                    { "pressure": str(weather_data.pressure) }
                )
            ))
        if weather_data.humidity is not None:
            embed.fields.append(EmbedField(
                name=self.__i18n_provider.get(
                    "extensions.eather.get_basic_weather_workflow.embed_field_humidity"
                ),
                value=self.__i18n_provider.get(
                    "extensions.eather.get_basic_weather_workflow.embed_field_humidity_value",
                    { "humidity": str(weather_data.humidity) }
                )
            ))

        if weather_data.condition.condition_image_url is not None:
            embed.thumbnail_url = weather_data.condition.condition_image_url

        return embed
