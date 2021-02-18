from holobot.bot_interface import BotInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.display.display_interface import DisplayInterface

class Discord(DisplayInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__bot = service_collection.get(BotInterface)

    async def send_dm(self, user_id: int, message: str):
        if not (user := self.__bot.get_user_by_id(user_id)):
            print(f"[Display] The user with the identifier '{user_id}' doesn't exist.")
            return
        await user.send(message)
