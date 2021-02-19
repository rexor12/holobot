from holobot.bot_interface import BotInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.display.display_interface import DisplayInterface
from holobot.logging.log_interface import LogInterface

class Discord(DisplayInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__bot = service_collection.get(BotInterface)
        self.__log = service_collection.get(LogInterface)

    async def send_dm(self, user_id: int, message: str):
        if not (user := self.__bot.get_user_by_id(user_id)):
            self.__log.warning(f"[Discord] Unexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        await user.send(message)
