import logging

from holobot.sdk.configs import IOptions
from holobot.sdk.integration import IIntegration
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from .bot import BotServiceInterface
from .discord_options import DiscordOptions

@injectable(IIntegration)
class Integration(IIntegration):
    def __init__(
        self,
        bot: BotServiceInterface,
        logger_factory: ILoggerFactory,
        options: IOptions[DiscordOptions]
    ) -> None:
        super().__init__()
        self.__bot: BotServiceInterface = bot
        self.__log = logger_factory.create(Integration)
        self.__options = options

    async def start(self) -> None:
        self.__log.debug("Starting Discord integration...")
        if self.__options.value.IsNetworkTraceEnabled:
            rest_logger = logging.getLogger("hikari.rest")
            rest_logger.setLevel("TRACE_HIKARI")

            gateway_logger = logging.getLogger("hikari.gateway")
            gateway_logger.setLevel("TRACE_HIKARI")

        await self.__bot.start()
        self.__log.info("Discord integration started")

    async def stop(self) -> None:
        self.__log.debug("Stopping Discord integration...")
        await self.__bot.stop()
        self.__log.info("Discord integration stopped")
