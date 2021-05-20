from .display_interface import DisplayInterface
# from .. import BotInterface
from ..dependency_injection import ServiceCollectionInterface
from ..logging import LogInterface
from holobot.bot_interface import BotInterface

class Discord(DisplayInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__bot = service_collection.get(BotInterface)
        self.__log = service_collection.get(LogInterface)

    async def send_dm(self, user_id: int, message: str):
        if not (user := self.__bot.get_user_by_id(user_id)):
            self.__log.warning(f"[Discord] Unexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        await user.send(message)
