from .bot import BotServiceInterface
from holobot.sdk.integration import IntegrationInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(IntegrationInterface)
class Integration(IntegrationInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__bot: BotServiceInterface = services.get(BotServiceInterface)
        self.__log: LogInterface = services.get(LogInterface).with_name("Discord", "Integration")

    async def start(self) -> None:
        self.__log.debug("[Integration] Starting Discord integration...")
        await self.__bot.start()
        self.__log.info("[Integration] Discord integration started.")
    
    async def stop(self) -> None:
        self.__log.debug("[Integration] Stopping Discord integration...")
        await self.__bot.stop()
        self.__log.info("[Integration] Discord integration stopped.")
