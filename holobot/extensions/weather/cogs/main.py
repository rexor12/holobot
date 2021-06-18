from .. import WeatherClientInterface
from ..exceptions import QueryQuotaExhaustedError
from ..models import WeatherData
from discord.embeds import Embed
from discord.ext.commands.cog import Cog
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.bot import Bot
from holobot.discord.sdk.utils import reply
from holobot.sdk.exceptions import InvalidOperationError

class Weather(Cog, name="Weather"):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.__weather_client: WeatherClientInterface = bot.service_collection.get(WeatherClientInterface)
    
    @cog_ext.cog_subcommand(base="weather", name="basic", description="Displays the current temperature in a city.", options=[
        create_option("city", "The name of the city.", SlashCommandOptionType.STRING, True)
    ])
    async def slash_remove(self, context: SlashContext, city: str):
        try:
            weather_data = await self.__weather_client.get_weather_data(city)
            if weather_data.temperature is None:
                await reply(context, "No information is available right now. Please, try again later.")
                return
            await reply(context, Weather.__create_embed(weather_data))
        except InvalidOperationError:
            await reply(context, "OpenWeather isn't configured. Please, contact your server administrator.")
            return
        except QueryQuotaExhaustedError:
            await reply(context, "The daily quota has been used up for the bot. Please, try again later or contact your server administrator.")
            return
    
    @staticmethod
    def __create_embed(weather_data: WeatherData) -> Embed:
        embed = Embed(
            title="Weather report", description=f"Information about the current weather in {weather_data.name}.", color=0xeb7d00
        ).add_field(
            name="Temperature", value=f"{weather_data.temperature:,.2f} °C"
        ).set_footer(text=f"Powered by OpenWeather")

        if weather_data.pressure is not None:
            embed.add_field(name="Pressure", value=f"{weather_data.pressure} hPa")
        if weather_data.humidity is not None:
            embed.add_field(name="Humidity", value=f"{weather_data.humidity}%")

        if weather_data.condition.condition_image_url is not None:
            embed.set_thumbnail(url=weather_data.condition.condition_image_url)
        return embed

def setup(bot: Bot):
    bot.add_cog(Weather(bot))
