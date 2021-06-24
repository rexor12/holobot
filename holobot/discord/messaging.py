from .bot import Bot
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(MessagingInterface)
class Messaging(MessagingInterface):
    # NOTE: This is a hack, because we have a circular dependency here.
    # Messages can be sent through an instance of Bot only, but
    # in our particular case, Bot uses cogs which use services
    # that require the messaging - which needs a Bot!
    # Therefore, as a hack, we're using this static field
    # to have a reference to our instance of Bot... at some point.
    # This could possibly be avoided if discord.py supported IoC.
    bot: Optional[Bot] = None

    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__log: LogInterface = services.get(LogInterface).with_name("Discord", "Messaging")
    
    async def send_dm(self, user_id: str, message: str) -> None:
        if Messaging.bot is None:
            self.__log.warning(f"Bot isn't initialized. {{ UserId = {user_id}, Operation = DM }}")
            return
        if not (user := Messaging.bot.get_user_by_id(int(user_id))):
            self.__log.warning(f"Inexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        await user.send(message)
