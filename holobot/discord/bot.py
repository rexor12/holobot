from .bot_interface import BotInterface
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.user import User
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.logging import LogInterface
from typing import Optional

import discord.ext.commands as commands

class Bot(commands.Bot, BotInterface):
	def __init__(self, services: ServiceCollectionInterface, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.service_collection: ServiceCollectionInterface = services
		self.__log: LogInterface = services.get(LogInterface)
	
	async def set_status_text(self, type: ActivityType, text: str, status: Status = None):
		await self.change_presence(
			activity=Activity(name=text, type=type),
			status=status
		)
	
	def get_user_by_id(self, user_id: int) -> Optional[User]:
		user = self.get_user(user_id)
		if user is None or not isinstance(user, User):
			return None
		return user
	
	async def send_dm(self, user_id: int, message: str) -> None:
		if not (user := self.get_user_by_id(user_id)):
			self.__log.warning(f"[Bot] Unexistent user. {{ UserId = {user_id}, Operation = DM }}")
			return
		await user.send(message)