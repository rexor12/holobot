from .. import WeatherClientInterface
from ..exceptions import InvalidLocationError, OpenWeatherError, QueryQuotaExhaustedError
from ..models import WeatherData
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError

@injectable(CommandInterface)
class GetBasicWeatherCommand(CommandBase):
    def __init__(self, weather_client: WeatherClientInterface) -> None:
        super().__init__("basic")
        self.__weather_client: WeatherClientInterface = weather_client
        self.group_name = "weather"
        self.description = "Displays the current temperature in a city."
        self.options = [
            Option("city", "The name of the city")
        ]
    
    async def execute(self, context: ServerChatInteractionContext, city: str) -> CommandResponse:
        try:
            weather_data = await self.__weather_client.get_weather_data(city)
            if weather_data.temperature is None:
                return CommandResponse(
                    action=ReplyAction(content="No information is available right now. Please, try again later.")
                )
            return CommandResponse(
                action=ReplyAction(content=GetBasicWeatherCommand.__create_embed(weather_data))
            )
        except InvalidLocationError:
            return CommandResponse(
                action=ReplyAction(content="The location you requested cannot be found. Did you make a typo?")
            )
        except OpenWeatherError as error:
            return CommandResponse(
                action=ReplyAction(content=f"An OpenWeather internal error has occurred (code: {error.error_code}). Please, try again later or contact your server administrator.")
            )
        except InvalidOperationError:
            return CommandResponse(
                action=ReplyAction(content="OpenWeather isn't configured. Please, contact your server administrator.")
            )
        except QueryQuotaExhaustedError:
            return CommandResponse(
                action=ReplyAction(content="The daily quota has been used up for the bot. Please, try again later or contact your server administrator.")
            )
        except CircuitBrokenError:
            return CommandResponse(
                action=ReplyAction(content="I couldn't communicate with OpenWeather. Please, wait a few minutes and try again.")
            )
    
    @staticmethod
    def __create_embed(weather_data: WeatherData) -> Embed:
        embed = Embed(
            title="Weather report",
            description=f"Information about the current weather in {weather_data.name}.",
            footer=EmbedFooter(
                text="Powered by OpenWeather",
                icon_url="https://openweathermap.org/themes/openweathermap/assets/img/mobile_app/android_icon.png")
        )
        embed.fields.append(EmbedField(
            name="Temperature",
            value=f"{weather_data.temperature:,.2f} °C"
        ))

        if weather_data.pressure is not None:
            embed.fields.append(EmbedField(name="Pressure", value=f"{weather_data.pressure} hPa"))
        if weather_data.humidity is not None:
            embed.fields.append(EmbedField(name="Humidity", value=f"{weather_data.humidity}%"))

        if weather_data.condition.condition_image_url is not None:
            embed.thumbnail_url = weather_data.condition.condition_image_url

        return embed
