from .bot import BotServiceInterface
from holobot.sdk.integration import IntegrationInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

@injectable(IntegrationInterface)
class Integration(IntegrationInterface):
    def __init__(
        self,
        bot: BotServiceInterface,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__bot: BotServiceInterface = bot
        self.__log = logger_factory.create(Integration)

    async def start(self) -> None:
        self.__log.debug("Starting Discord integration...")
        await self.__bot.start()
        self.__log.info("Discord integration started")
    
    async def stop(self) -> None:
        self.__log.debug("Stopping Discord integration...")
        await self.__bot.stop()
        self.__log.info("Discord integration stopped")
