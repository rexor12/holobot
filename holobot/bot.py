from .bot_interface import BotInterface
from .dependency_injection import ServiceCollectionInterface
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.user import User

import discord.ext.commands as commands

class Bot(commands.Bot, BotInterface):
	def __init__(self, service_collection: ServiceCollectionInterface, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.service_collection: ServiceCollectionInterface = service_collection
	
	async def set_status_text(self, type: ActivityType, text: str, status: Status = None):
		await self.change_presence(
			activity=Activity(name=text, type=type),
			status=status
		)
		
	def get_user_by_id(self, user_id: int) -> User:
		return self.get_user(user_id)
